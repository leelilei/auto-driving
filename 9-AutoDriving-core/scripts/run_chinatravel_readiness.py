"""Constraint-aware six-case readiness run with explicit clarification states.
No model imports/calls. Never overwrite original collection or original search results.
"""
import argparse,contextlib,copy,hashlib,io,json,math,time
from pathlib import Path
import chinatravel_pipeline_v3 as ct
import chinatravel_parse_plan_v4 as parser
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'

def native(value):
    import numpy as np
    if isinstance(value,np.generic):return native(value.item())
    if isinstance(value,dict):return {k:native(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [native(v) for v in value]
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('Nonfinite value')
    if value is None or type(value) in (int,float,bool,str):return value
    raise TypeError('Unsupported JSON type: '+type(value).__name__)

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(native(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def score(queries,predictions):
    with ct.offline(),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        return ct.json_safe(ct.v1.evaluate(queries,predictions))

def run(out):
    from chinatravel_symbolic_backend import TracedWorldEnv,NoModel
    from chinatravel_ready_backend import ConstraintAwareAgent,requirements
    from chinatravel_parse_plan import evaluation_query
    out.mkdir(parents=True,exist_ok=False)
    public=ct.read(SOURCE/'public_inputs.json');ids=[p['uid'] for p in public]
    report=ct.read(SOURCE/'collection_deepseek_report.json');records={r['uid']:r for r in report['records']}
    if len(records)!=6 or set(records)!=set(ids):raise ValueError('Six-case evidence incomplete')
    original={};revised={};rows=[]
    write(out/'plan.json',{'ids':ids,'scope':'offline engineering rerun of three resolved intents, not new model samples',
       'new_model_calls':0,'per_case_seconds':30,'search_width':10,'change':'carry predicted budget/rooms into existing pruning hooks; deterministic price-first transport ranking; explicit clarification; no defaults or gold feedback',
       'source_hashes':{str(p.relative_to(ROOT)):ct.sha(p) for p in [SOURCE/'collection_deepseek_report.json',SOURCE/'public_inputs.json',Path(__file__),ROOT/'9-AutoDriving-core/scripts/chinatravel_parse_plan_v4.py',ROOT/'9-AutoDriving-core/scripts/chinatravel_symbolic_backend.py',ROOT/'9-AutoDriving-core/scripts/chinatravel_ready_backend.py']}})
    for item in public:
        uid=item['uid'];record=records[uid];intent=record.get('parsed_intent');old=SOURCE/'stage4_deepseek_planning'/uid/'raw_search_return.json'
        original[uid]=ct.read(old) if old.exists() else {};revised[uid]={}
        row={'uid':uid,'original_query':item['nature_language'],'parser_status':record['status']}
        try:
            parser.validate(intent,item['nature_language']);clauses=parser.compile_extended(intent)
        except Exception as exc:
            row.update(status='NEEDS_CLARIFICATION',missing_fields=[k for k in ('start_city','target_city','days','people_number') if not intent or intent.get(k) is None],error_type=type(exc).__name__)
            rows.append(row);continue
        d=out/'search'/uid;d.mkdir(parents=True)
        q={k:intent[k] for k in ('start_city','target_city','days','people_number')};q.update(uid=uid,hard_logic_py=clauses)
        write(d/'predicted_constraints.json',q)
        started=time.monotonic();plan={};success=False
        with (d/'search.log').open('w') as log,(d/'tool_trace.jsonl').open('w') as trace,ct.offline(),contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            env=TracedWorldEnv(trace);agent=ConstraintAwareAgent(intent=intent,env=env,backbone_llm=NoModel(),cache_dir=str(d/'cache'),log_dir=str(d/'logs'),search_width=10,debug=False);agent.TIME_CUT=30
            try:
                with ct.deadline(30):success,plan=agent.symbolic_search(copy.deepcopy(q))
                status='search_success' if success else 'search_failed'
            except Exception as exc:status='search_error:'+type(exc).__name__
        converted=native(plan)
        write(d/'candidate.json',converted)
        if success:revised[uid]=converted
        row.update(status=status,seconds=time.monotonic()-started,tool_calls=len(env.results),raw_schema_valid=ct.valid_plan(plan),json_schema_valid=ct.valid_plan(converted),normalization_changed_native_types=type(plan)!=type(converted) or ct.valid_plan(plan)!=ct.valid_plan(converted))
        rows.append(row)
    # Independent scoring phase only now reads canonical gold, never feeds back to search.
    queries={uid:evaluation_query(uid) for uid in ids}
    original_score=score(queries,original);new_score=score(queries,revised)
    write(out/'original_predictions.json',original);write(out/'predictions.json',revised)
    write(out/'original_official_score.json',original_score);write(out/'official_score.json',new_score)
    write(out/'rows.json',rows)
    usage={k:sum(r.get('provider_response',{}).get('usage',{}).get(k,0) for r in records.values()) for k in ('prompt_tokens','completion_tokens','total_tokens')}
    summary={'n_expected':6,'original_unique_model_requests':6,'new_model_requests':0,'requested_model':'deepseek-v4-flash','returned_models':sorted({r['provider_response']['model'] for r in records.values()}),'original_usage':usage,'original_all_pass_rate':original_score['all_pass_rate'],'rerun_all_pass_rate':new_score['all_pass_rate'],'rows':rows}
    write(out/'summary.json',summary)
    write(out/'hashes.json',{str(p.relative_to(out)):ct.sha(p) for p in out.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'},ensure_ascii=False))

def replay(out):
    from chinatravel_parse_plan import evaluation_query
    pins=ct.read(out/'plan.json');hashes=ct.read(out/'hashes.json')
    required={'plan.json','summary.json','rows.json','predictions.json','original_predictions.json','official_score.json','original_official_score.json'}
    if not required<=set(hashes):raise ValueError('Required artifacts missing')
    for name,digest in hashes.items():
        if ct.sha(out/name)!=digest:raise ValueError('Artifact changed: '+name)
    for name,digest in pins['source_hashes'].items():
        if ct.sha(ROOT/name)!=digest:raise ValueError('Source changed: '+name)
    with ct.offline():
        q={uid:evaluation_query(uid) for uid in pins['ids']}
        for prefix in ('','original_'):
            predictions=ct.read(out/(prefix+'predictions.json'))
            if set(predictions)!=set(q):raise ValueError('Missing/extra IDs')
            if score(q,predictions)!=ct.read(out/(prefix+'official_score.json')):raise ValueError('Score changed')
    print('Offline replay PASS: original and rerun, complete six-case denominator')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','replay']);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    (run if a.mode=='run' else replay)(a.out.resolve())
