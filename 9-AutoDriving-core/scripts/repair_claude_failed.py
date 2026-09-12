"""One bounded recovery pass over failed calls; originals remain untouched."""
import argparse,hashlib,json
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from pathlib import Path
import resume_claude_full160 as recovery

base = recovery.base

def repair(u, reference, source, out, config):
    uid = u['utterance_id']
    cp = out/'completion_checkpoints'/uid
    cp.mkdir(parents=True,exist_ok=True)
    final = out/'utterances'/(uid+'.json')
    if final.exists():
        return uid
    # Preseed only successful original calls, preserving their exact raw output.
    for call in u['calls'].values():
        if not call.get('schema_valid'):
            continue
        key=hashlib.sha256(json.dumps([call['system_prompt'],call['user_prompt']]).encode()).hexdigest()
        p=cp/(key+'_0.json')
        if not p.exists():
            usage=call.get('usage')
            base.write_json(p,{'system':call['system_prompt'],'user':call['user_prompt'],
                              'raw':call['raw_response'],'usage':usage.get('raw',usage) if usage else None,
                              'response':{'model':call.get('returned_model')},'reused_original':True})
    recovery.CTX.directory=cp
    graph=base.SyntheticGraph.load(source/(u['group_id']+'_graph.json'))
    row=base.run_utterance(reference,graph,base.ExactRouteSolver(graph),config)
    row['recovery_note']='Separate recovery pass; not substituted into primary original-run results.'
    base.write_json(final,row)
    return uid

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=4)
    a=ap.parse_args()
    out=a.source/'recovery_repairs'
    out.mkdir(exist_ok=True)
    refs={u['utterance_id']:u for u in json.loads((base.ROOT/'data/test/test_640_utterances.json').read_text())}
    failed=[]
    for p in sorted(a.source.glob('test_*.json')):
        if p.name.endswith('_graph.json'):continue
        for u in json.loads(p.read_text())['utterances']:
            if any(not u['calls'].get(m,{}).get('schema_valid') for m in ['A','B','review']):failed.append(u)
    base.write_json(out/'plan.json',{'failed_utterances':[u['utterance_id'] for u in failed],
        'policy':'One recovery pass, original valid calls reused; max 3 outer attempts per failed method, existing transport retry policy retained. No retries for semantically wrong but schema-valid outputs.'})
    config=base.load_config(a.config)
    config=replace(config,retries=3,retry_sleep=2.0,timeout=max(config.timeout,90))
    base.LLM=recovery.CheckpointLLM
    errors=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        fs={pool.submit(repair,u,refs[u['utterance_id']],a.source,out,config):u['utterance_id'] for u in failed}
        for f in as_completed(fs):
            try: print('recovered_record',f.result(),flush=True)
            except Exception as e: errors.append({'uid':fs[f],'type':type(e).__name__})
    base.write_json(out/'status.json',{'planned':len(failed),'saved':len(list((out/'utterances').glob('*.json'))),'errors':errors})
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
