"""Fresh, version-bound collection; no overwrite/resume/retries; no paper generation.
Stage 3 requires an explicitly supplied passing admission JSON.
"""
from pathlib import Path
import argparse, json, hashlib, sys, time
from dataclasses import asdict, replace
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.llm_client import LLM, load_config
from src.intent import Intent
from src.graph import generate_synthetic_graph
from src.solver import ExactRouteSolver
from src.evaluation import check_route
from src.gating import execute_method_decision, calculate_route_regret
from src.metrics import compute_tsr,compute_gtsr,compute_route_flip
from scripts.run_main_experiment import PROMPTS

def sha(data): return hashlib.sha256(data).hexdigest()
def write(path,data):
    with path.open('x',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False,allow_nan=False)
def stamp():return datetime.now(timezone.utc).isoformat()
def validate(data,expected):
    if len(data)!=expected or len({u['utterance_id'] for u in data})!=expected:raise ValueError('Wrong/duplicate utterance count')
    groups={}
    for u in data:
        groups.setdefault(u['group_id'],[]).append(u)
        if u['preference_direction'] not in {'quality_first','balanced','distance_first'}:raise ValueError('Unclear/missing direction requires separate evaluation handling')
        Intent.parse(dict(u['gold_hard'],quality_weight=.5))
    if any(sorted(x['variant_type'] for x in us)!=['V0','V1','V2','V3'] for us in groups.values()):raise ValueError('Each group requires unique V0..V3')
    return groups

def run_group(us,cfg,directory,stage):
    gid=us[0]['group_id'];graph=generate_synthetic_graph(graph_id=gid+'_graph',seed=(1000 if stage=='pilot' else 5000)+int(gid.split('_')[-1]))
    write(directory/(gid+'_graph.json'),graph.to_dict());solver=ExactRouteSolver(graph);out=[]
    for rec in us:
        uid=rec['utterance_id'];gold=Intent.parse(dict(rec['gold_hard'],quality_weight={'quality_first':.75,'balanced':.5,'distance_first':.25}[rec['preference_direction']]))
        oracle=solver.solve(**gold.solver_args());u=dict(group_id=gid,utterance_id=uid,variant_type=rec['variant_type'],text=rec['text'],source_index=rec['source_index'],preference_direction=rec['preference_direction'],gold_intent=asdict(gold),oracle_route=asdict(oracle),oracle_check=check_route(graph,oracle,gold),calls={},candidates={},routes={})
        for name in (['A','B','review'] if stage=='pilot' else ['A','B','review','A2','A3']):
            system=PROMPTS['A' if name in ['A2','A3'] else name]
            user=rec['text'] if name!='review' else json.dumps({'instruction':rec['text'],'candidate_A':u['candidates'].get('A'),'candidate_B':u['candidates'].get('B')},ensure_ascii=False)
            call=dict(method=name,attempt=1,system_prompt=system,user_prompt=user,request_sha256=sha((system+'\0'+user).encode()),started_at=stamp())
            write(directory/'attempts'/(uid+'_'+name+'_started.json'),call)
            llm=LLM(cfg);candidate=None
            try:
                raw=llm.complete(system,user);call['raw_response']=raw
                try:candidate=Intent.parse(json.loads(raw));call['schema_valid']=True
                except (ValueError,TypeError) as exc:call.update(schema_valid=False,parse_error=str(exc))
            except Exception as exc:
                call.update(schema_valid=False,transport_error_type=type(exc).__name__,error_message=str(exc))
            call.update(finished_at=stamp(),telemetry=llm.telemetry[-1] if llm.telemetry else None)
            write(directory/'attempts'/(uid+'_'+name+'_finished.json'),call)
            u['calls'][name]=call;u['candidates'][name]=asdict(candidate) if candidate else None
            if name!='review':u['routes'][name]=asdict(solver.solve(**candidate.solver_args())) if candidate else None
            if 'transport_error_type' in call:break
        out.append(u)
        if any('transport_error_type' in c for c in u['calls'].values()):break
    write(directory/(gid+'.json'),dict(group_id=gid,utterances=out))
    return out,graph

def evaluate(all_us,graphs,params,stage):
    methods=['B0','B2','B3','B4','B5','B6','Ours']+(['B1'] if stage=='main' else [])
    from src.solver import RouteResult
    records={m:[] for m in methods}
    for u in all_us:
        graph=graphs[u['group_id']];solver=ExactRouteSolver(graph);gold=Intent.parse(u['gold_intent'])
        c={k:Intent.parse(v) if v else None for k,v in u['candidates'].items()};r={k:RouteResult(**v) if v else None for k,v in u['routes'].items()}
        for m in methods:
            _,route,meta=execute_method_decision(m,c,r,graph,solver,tau=params['tau_star'],tau_sem=params['tau_sem_star'],p_review=params['p_review_star'],group_id=u['group_id'],utterance_id=u['utterance_id'])
            check=check_route(graph,route,gold)
            # Flip requires task success on both sides, per revised protocol.
            rd=asdict(route) if route else None
            if rd:rd['is_valid']=check['task_success']
            selected=['A'] if m=='B0' else ['A','A2','A3'] if m=='B1' else ['A','B']+(['review'] if meta['review_triggered'] else [])
            telem=[u['calls'].get(k,{}).get('telemetry') or {} for k in selected]
            records[m].append(dict(group_id=u['group_id'],utterance_id=u['utterance_id'],variant_type=u['variant_type'],task_success=check['task_success'],reasons=check['reasons'],route=rd,regret=calculate_route_regret(graph,u['oracle_route'],route,gold.quality_weight) if check['task_success'] else None,meta=meta,selected_calls=selected,known_provider_tokens=sum(t.get('total_tokens',0) for t in telem if t.get('usage_source')=='provider'),usage_complete=all(t.get('usage_source')=='provider' for t in telem)))
    metrics={}
    for m,rs in records.items():
        regret=[r['regret'] for r in rs if r['regret'] is not None]
        metrics[m]=dict(TSR=compute_tsr(rs),GTSR=compute_gtsr(rs),flip=compute_route_flip(rs),regret=sum(regret)/len(regret) if regret else None,regret_n=len(regret),review_rate=sum(r['meta']['review_triggered'] for r in rs)/len(rs),mean_calls=sum(len(r['selected_calls']) for r in rs)/len(rs),known_provider_tokens=sum(r['known_provider_tokens'] for r in rs),usage_complete=all(r['usage_complete'] for r in rs))
    assert all((a['route'],a['task_success'])==(b['route'],b['task_success']) for a,b in zip(records['B0'],records['B2']))
    return metrics,records

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['pilot','main'],required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--dry-run',action='store_true');p.add_argument('--admission',type=Path);args=p.parse_args()
    data_bytes=args.dataset.read_bytes();data=json.loads(data_bytes);groups=validate(data,80 if args.stage=='pilot' else 640)
    cfg=replace(load_config(ROOT/'configs/llm_config.json'),retries=0,timeout=45,max_output_tokens=1600,max_concurrency=args.workers)
    if cfg.provider=='mock':raise ValueError('Real collection requires non-mock provider')
    params=json.loads((ROOT/'data/calibration/frozen_config.json').read_text())['calibrated_parameters']
    plan=dict(stage=args.stage,dataset=str(args.dataset),dataset_sha256=sha(data_bytes),groups=len(groups),utterances=len(data),max_attempts=len(data)*(3 if args.stage=='pilot' else 5),retries=0,config=asdict(cfg),parameters=params,scope='fresh replication on previously exposed intent groups; NOT an untouched confirmatory holdout',evaluation_weight_map={'quality_first':.75,'balanced':.5,'distance_first':.25},metric_version='fresh-v3-valid-task-pairs')
    if args.dry_run:print(json.dumps(plan,indent=2));return
    if args.stage=='main':
        if not args.admission:raise ValueError('Main requires independently approved admission')
        admission=json.loads(args.admission.read_text())
        if admission.get('stage3_allowed') is not True or admission.get('test_dataset_sha256')!=sha(data_bytes):raise ValueError('Stage 3 admission missing or dataset hash mismatch')
        plan['admission']=admission
    d=ROOT/'results/runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_fresh_'+args.stage);d.mkdir(exist_ok=False);(d/'attempts').mkdir();(d/'source').mkdir()
    (d/'dataset.json').write_bytes(data_bytes)
    for source in [*sorted((ROOT/'src').glob('*.py')),Path(__file__),ROOT/'scripts/run_main_experiment.py']:
        (d/'source'/source.name).write_bytes(source.read_bytes())
    plan['source_sha256']={q.name:sha(q.read_bytes()) for q in (d/'source').iterdir()};plan['started_at']=stamp();write(d/'manifest.json',plan);print('RUN_DIR='+str(d),flush=True)
    all_us=[];graphs={};items=[groups[g] for g in sorted(groups)];start=time.monotonic();stopped=False
    # Bounded batches stop expansion on provider failure; all attempted failures retained.
    for offset in range(0,len(items),args.workers):
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            batch=list(pool.map(lambda us:run_group(us,cfg,d,args.stage),items[offset:offset+args.workers]))
        for us,graph in batch:all_us.extend(us);graphs[us[0]['group_id']]=graph
        calls=[c for us,_ in batch for u in us for c in u['calls'].values()]
        errors=sum('transport_error_type' in c for c in calls)
        print(f'groups={len(graphs)}/{len(groups)} attempts={sum(len(u["calls"]) for u in all_us)} batch_transport_errors={errors}',flush=True)
        if errors:stopped=True;break
    metrics,records=evaluate(all_us,graphs,params,args.stage);calls=[c for u in all_us for c in u['calls'].values()];tel=[c.get('telemetry') or {} for c in calls]
    summary=dict(run_id=d.name,collection_complete=not stopped and len(all_us)==len(data),evaluated_utterances=len(all_us),planned_utterances=len(data),unattempted_utterances=len(data)-len(all_us),transport_errors=sum('transport_error_type' in c for c in calls),schema_valid=sum(c.get('schema_valid',False) for c in calls),attempts=len(calls),known_provider_tokens=sum(t.get('total_tokens',0) for t in tel if t.get('usage_source')=='provider'),usage_missing=sum(t.get('usage_source')!='provider' for t in tel),wall_seconds=time.monotonic()-start,metrics=metrics)
    write(d/'predictions.json',records);write(d/'summary.json',summary)
    write(d/'integrity.json',{str(q.relative_to(d)):sha(q.read_bytes()) for q in sorted(d.rglob('*')) if q.is_file()})
    print(json.dumps(summary,indent=2),flush=True)
    if not summary['collection_complete']:raise SystemExit(2)
if __name__=='__main__':main()
