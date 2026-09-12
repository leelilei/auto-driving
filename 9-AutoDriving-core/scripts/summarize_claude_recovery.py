"""Read-only collection accounting, independent of legacy experiment summaries."""
import json,hashlib
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNS={'haiku':'20260912T112707Z_main_test_claude-haiku-4-5-20251001_full160',
      'sonnet':'20260912T135800Z_main_test_claude-sonnet-4-6_full160'}
DOC=ROOT.parent/'docs/experiments/v41_codex_audit_20260912/closeout/claude_resume_20260912'

def account(rows):
    c=Counter();failed=[]
    for u in rows:
        c['utterances']+=1
        bad=False
        for method in ['A','B','review']:
            call=u.get('calls',{}).get(method,{})
            c['method_slots']+=1
            if call.get('schema_valid'):
                c['schema_valid']+=1
            else:
                bad=True
                kind='skipped' if call.get('review_skipped_missing_candidates') else 'raw_parse_failure' if call.get('raw_response') else 'empty_or_transport_failure'
                c[kind]+=1
                failed.append({'uid':u['utterance_id'],'method':method,'kind':kind})
            if call.get('raw_response'):c['retained_nonempty_responses']+=1
            usage=call.get('usage')
            if usage is not None:c['retained_provider_tokens']+=usage.get('total_tokens',0)
            elif not call.get('review_skipped_missing_candidates'):c['missing_usage_slots']+=1
        c['all_three_schema_valid_utterances']+=not bad
    return {'counts':dict(c),'failed_slots':failed}

def main():
    references={u['utterance_id']:u for u in json.loads((ROOT/'data/test/test_640_utterances.json').read_text())}
    all_results={}
    old=json.loads((DOC/'existing_assets_sha256.json').read_text())
    for model,name in RUNS.items():
        p=ROOT/'results/runs'/name
        files=sorted(f for f in p.glob('test_*.json') if not f.name.endswith('_graph.json'))
        rows=[u for f in files for u in json.loads(f.read_text())['utterances']]
        result=account(rows)
        result.update(groups=len(files),run_dir=str(p),unique_ids=len({u['utterance_id'] for u in rows}),
            text_matches=sum(u['text']==references[u['utterance_id']]['text'] for u in rows),
            missing_ids=sorted(set(references)-{u['utterance_id'] for u in rows}))
        result['existing_assets_unchanged']=all((p/n).exists() and hashlib.sha256((p/n).read_bytes()).hexdigest()==h for n,h in old[name].items())
        rp=p/'recovery_repairs/utterances'
        repaired=[json.loads(f.read_text()) for f in rp.glob('*.json')]
        result['repair_records']=account(repaired)
        overlays={u['utterance_id']:u for u in repaired}
        result['recovery_combined']=account([overlays.get(u['utterance_id'],u) for u in rows])
        cps=[f for f in p.glob('completion_checkpoints/*/*.json') if f.name!='utterance.json']
        cps += list(p.glob('recovery_repairs/completion_checkpoints/*/*.json'))
        calls=[json.loads(f.read_text()) for f in cps]
        calls=[x for x in calls if not x.get('reused_original')]
        result['checkpointed_completion_calls']=len(calls)
        result['checkpointed_completion_errors']=sum('error' in x for x in calls)
        result['checkpointed_response_tokens']=sum((x.get('usage') or {}).get('input_tokens',(x.get('usage') or {}).get('prompt_tokens',0))+(x.get('usage') or {}).get('output_tokens',(x.get('usage') or {}).get('completion_tokens',0)) for x in calls)
        result['cost_note']='Provider token records only; nested transport attempts and overwritten historical retries may be missing. No verified monetary charge available. Repaired outcomes are a separate recovery cohort.'
        all_results[model]=result
    DOC.mkdir(exist_ok=True)
    (DOC/'collection_status.json').write_text(json.dumps(all_results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:{'groups':v['groups'],'original':v['counts'],'repair':v['repair_records']['counts'],'existing_unchanged':v['existing_assets_unchanged']} for k,v in all_results.items()},ensure_ascii=False))

if __name__=='__main__':main()
