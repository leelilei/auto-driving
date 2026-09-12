"""Frozen 180-unit Scene-Rule30 development collection and offline reconstruction."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import math
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import threading

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.scene_pilot12 import read,write,digest,now,NetworkBlocker
from scripts.scene_haiku_contract import contracted_request as request
from scripts.prepare_scene_pilot12 import solve
from src.scene_policy import Policy,parse_response,execute,evaluate
from src.llm_client import LLM,load_config

DATA=ROOT/'data/scene_rule30_candidate'
ROLES=('direct','language','evidence')
TERMINAL={'COMPLETE','SCHEMA_FAILED','UPSTREAM_SCHEMA_FAILED'}

def verify(run):
    m=read(run/'manifest.json')
    for f,h in m['files'].items():
        if digest(run/f)!=h:raise ValueError('changed frozen input: '+f)
    for f,h in m['sources'].items():
        if digest(ROOT/f)!=h or digest(run/'source'/f)!=h:raise ValueError('changed source: '+f)
    plan=read(run/'run_plan.json');public=read(run/'model_inputs.json')
    if len(public)!=30 or len({c['case_id'] for c in public})!=30:raise ValueError('expected 30 unique cases')
    expected={(c['case_id'],rep,role) for c in public for rep in (1,2) for role in ROLES}
    if len(plan)!=180 or {(j['case_id'],j['rep'],j['role']) for j in plan}!=expected:raise ValueError('invalid 180-unit plan')
    if any(j['call_id']!=f"{j['case_id']}__r{j['rep']}__{j['role']}" for j in plan):raise ValueError('invalid call id')
    return m

def prepare(run,concurrency,mode='REAL'):
    if not 1<=concurrency<=16:raise ValueError('concurrency must be 1..16')
    if run.exists():raise ValueError('refuse overwrite')
    original=read(DATA/'manifest.json')
    for f,h in original['files'].items():
        if digest(DATA/f)!=h:raise ValueError('candidate dataset changed')
    run.mkdir(parents=True)
    files={}
    for name in original['files']:
        shutil.copyfile(DATA/name,run/name);files[name]=digest(run/name)
    config=read(ROOT/'configs/scene_xcode_haiku.json')
    config.update(retries=0,max_concurrency=1,timeout=120,max_output_tokens=1600)
    write(run/'config.json',config);files['config.json']=digest(run/'config.json')
    sources={}
    for f in ['scripts/scene_rule30_run.py','scripts/scene_pilot12.py','scripts/scene_haiku_contract.py',
              'scripts/prepare_scene_pilot12.py','scripts/experiment.py','src/scene_policy.py','src/llm_client.py']:
        dest=run/'source'/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dest);sources[f]=digest(dest)
    write(run/'manifest.json',dict(protocol='scene-rule30-v1',mode=mode,created=now(),files=files,sources=sources,
          scope='UNREVIEWED_DEVELOPMENT_ONLY' if mode=='REAL' else 'MOCK_ENGINEERING_ONLY',human_review='PENDING',
          authorization='用户：推进180次调用，需要扩大并发加快试验速度。',
          planned=180,concurrency=concurrency,max_recoveries=18,max_attempts_per_unit=2,
          prompt_revision='scene-haiku-explicit-object-v1',stopping='401/403/429 or exhausted transport recovery stops launch; no semantic retries'))
    (run/'attempts').mkdir();verify(run)

def records(run,cid):return [read(p) for p in sorted((run/'attempts').glob(cid+'.a*.json'))]

def latest(run,cid):
    rs=records(run,cid)
    if any(r['status']=='STARTED' for r in rs):raise ValueError('unreconciled STARTED request')
    return rs[-1] if rs else None

def collect(run,client_factory=LLM):
    m=verify(run);real=m['mode']=='REAL';config=load_config(run/'config.json')
    if real and not os.environ.get(config.api_key_env):
        r=subprocess.run(['security','find-generic-password','-s',config.api_key_env,'-w'],capture_output=True,text=True,check=True)
        os.environ[config.api_key_env]=r.stdout.strip()
    stop=threading.Event();lock=threading.Lock();recoveries=len(list((run/'attempts').glob('*.a2.json')))
    def call(case,rep,role,candidate):
        nonlocal recoveries
        cid=f"{case['case_id']}__r{rep}__{role}";old=latest(run,cid)
        if old and old['status'] in TERMINAL:return old
        payload=request(case,role,candidate)
        start=len(records(run,cid))+1
        for attempt in range(start,3):
            if stop.is_set():return None
            if attempt==2:
                with lock:
                    if recoveries>=m['max_recoveries']:stop.set();return None
                    recoveries+=1
            record=dict(call_id=cid,case_id=case['case_id'],rep=rep,role=role,request=payload,
                        status='STARTED',source=m['mode'],started=now())
            path=run/'attempts'/f'{cid}.a{attempt}.json';write(path,record);llm=None
            try:
                if real:
                    llm=client_factory(config);raw=llm.complete(**payload)
                    record.update(telemetry=llm.telemetry[-1],provider_response=getattr(llm.client,'last_response',None))
                else:
                    raw='{"selection":"nearest_from_bank","availability_reference":"arrival","return_by":null,"evidence":{}}'
                    record['telemetry']={'usage_source':'mock','latency_seconds':0}
                record['raw_response']=raw;policy,_=parse_response(raw)
                record.update(status='COMPLETE',parsed_policy=policy.to_dict())
            except Exception as e:
                if llm and llm.telemetry:record['telemetry']=llm.telemetry[-1]
                message=str(e)
                key=os.environ.get(config.api_key_env)
                if key:message=message.replace(key,'[REDACTED]')
                record.update(status='SCHEMA_FAILED' if 'raw_response' in record else 'TRANSPORT_FAILED',error_type=type(e).__name__,error=message)
            record['finished']=now();write(path,record)
            if record['status'] in TERMINAL:return record
            if any(f'HTTP {code}' in record.get('error','') for code in (401,403,429)):stop.set();return record
            old=record
        return old
    def unit(case,rep):
        if stop.is_set():return
        direct=call(case,rep,'direct',None)
        if not direct or direct['status']=='TRANSPORT_FAILED':stop.set();return
        if direct['status']=='SCHEMA_FAILED':
            for role in ('language','evidence'):
                cid=f"{case['case_id']}__r{rep}__{role}";path=run/'attempts'/f'{cid}.a1.json'
                if not path.exists():write(path,dict(call_id=cid,case_id=case['case_id'],rep=rep,role=role,source=m['mode'],status='UPSTREAM_SCHEMA_FAILED'))
            return
        candidate=Policy.parse(direct['parsed_policy'])
        for role in (('language','evidence') if rep==1 else ('evidence','language')):
            out=call(case,rep,role,candidate)
            if not out or out['status']=='TRANSPORT_FAILED':stop.set();return
    public=read(run/'model_inputs.json')
    # Three requests within the 180-unit plan test the real chain before parallel work.
    unit(public[0],1)
    jobs=[(c,rep) for rep in (1,2) for c in public if not (rep==1 and c==public[0])]
    if not stop.is_set():
        with ThreadPoolExecutor(max_workers=m['concurrency']) as pool:
            futures=[pool.submit(unit,*job) for job in jobs]
            for i,f in enumerate(as_completed(futures),2):
                f.result()
                if i%5==0 or i==60:print(f'Completed units {i}/60',flush=True)
    if stop.is_set():
        write(run/'collection_status.json',dict(status='INCOMPLETE_TRANSPORT',complete=False))
        raise RuntimeError('Collection incomplete; inspect failures before resuming')
    result=replay(run);write(run/'summary.json',result)
    print(result['methods'],flush=True)

def replay(run):
    m=verify(run);plan=read(run/'run_plan.json');valid_ids={j['call_id'] for j in plan}
    files=list((run/'attempts').glob('*.json'));all_records=[read(p) for p in files]
    if any(r.get('call_id') not in valid_ids or r.get('source')!=m['mode'] for r in all_records):raise ValueError('unknown call or provenance')
    if any(p.name not in (r['call_id']+'.a1.json',r['call_id']+'.a2.json') for p,r in zip(files,all_records)):
        raise ValueError('unexpected ledger filename')
    resolved={};parsed={};recoveries=0
    for j in plan:
        cid=j['call_id'];paths=sorted((run/'attempts').glob(cid+'.a*.json'));rs=records(run,cid)
        if not 1<=len(rs)<=2:raise ValueError('missing or excess attempts')
        recoveries+=len(rs)-1
        for i,(p,r) in enumerate(zip(paths,rs),1):
            if p.name!=f'{cid}.a{i}.json' or any(r.get(k)!=j[k] for k in ('call_id','case_id','rep','role')):raise ValueError('invalid identity')
            if i<len(rs) and r['status']!='TRANSPORT_FAILED':raise ValueError('illegal retry')
        r=rs[-1]
        if r['status'] not in TERMINAL:raise ValueError('incomplete logical unit')
        resolved[cid]=r
        if r['status']=='COMPLETE':
            p,_=parse_response(r['raw_response'])
            if p.to_dict()!=r['parsed_policy']:raise ValueError('saved parse differs from original')
            parsed[cid]=p
        elif r['status']=='SCHEMA_FAILED':
            try:parse_response(r['raw_response'])
            except (ValueError,TypeError):pass
            else:raise ValueError('valid output labelled schema failure')
    if recoveries>m['max_recoveries']:raise ValueError('recovery budget exceeded')
    public={c['case_id']:c for c in read(run/'model_inputs.json')}
    gold={g['case_id']:g for g in read(run/'gold_and_traces.json')}
    authors={c['case_id']:c for c in read(run/'author_review_cases.json')};rows=[];independent=0
    for j in plan:
        cid=j['call_id'];case=public[j['case_id']];r=resolved[cid]
        direct_id=f"{j['case_id']}__r{j['rep']}__direct";direct=parsed.get(direct_id)
        if r['status']=='UPSTREAM_SCHEMA_FAILED':
            if j['role']=='direct' or resolved[direct_id]['status']!='SCHEMA_FAILED':raise ValueError('invalid skip')
        else:
            expected=request(case,j['role'],direct if j['role']!='direct' else None)
            if any(a.get('request')!=expected for a in records(run,cid)):raise ValueError('frozen request mismatch')
        raw=parsed.get(cid);effective=raw or (direct if j['role']!='direct' else None)
        d=execute(case['scene'],effective) if effective else None
        if d is not None:
            assert case['scene']['speed_units_per_minute']==1
            ref=solve(case['scene'],effective.to_dict())
            if d!=dict(status=ref['status'],selected_poi_ids=sorted(ref['accepted_poi_ids'])):raise ValueError('independent decision mismatch')
            independent+=1
        g=gold[j['case_id']];score=evaluate(effective,d,g)
        base=evaluate(direct,execute(case['scene'],direct) if direct else None,g)
        block=authors[j['case_id']]['block_id']
        rows.append(dict(**j,block_id=block,stratum='primary' if block.startswith('G') else 'control',
             status=r['status'],policy=effective.to_dict() if effective else None,decision=d,
             raw_rule_correct=raw is not None and raw.to_dict()==g['policy'],
             fallback=j['role']!='direct' and raw is None and direct is not None,
             corrected=not base['object_success'] and score['object_success'],damaged=base['object_success'] and not score['object_success'],**score))
    fields=('rule_correct','raw_rule_correct','object_success','feasible_success','false_infeasible','fallback','corrected','damaged')
    def stats(subset):return {role:dict(n=sum(r['role']==role for r in subset),**{k:sum(r[k] for r in subset if r['role']==role) for k in fields}) for role in ROLES}
    calls=[r for r in all_records if r['status']!='UPSTREAM_SCHEMA_FAILED'];cost={}
    for role in ROLES:
        rs=[r for r in calls if r['role']==role]
        us=[r['provider_response']['usage'] for r in rs if (r.get('provider_response') or {}).get('usage') is not None]
        sums={k:sum(u.get(k,0) for u in us) for k in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')}
        ls=sorted(r['telemetry']['latency_seconds'] for r in rs if r.get('telemetry'))
        cost[role]=dict(physical_calls=len(rs),provider_usage_records=len(us),usage_unknown=len(rs)-len(us),**sums,
                       token_components_sum=sum(sums.values()),median_seconds=statistics.median(ls) if ls else None,
                       p95_seconds=ls[math.ceil(.95*len(ls))-1] if ls else None)
    times=[(datetime.fromisoformat(r['started']),datetime.fromisoformat(r['finished'])) for r in calls]
    return dict(scope=m['scope'],human_review='PENDING',complete=True,logical_units=len(plan),physical_calls=len(calls),
           recoveries=recoveries,concurrency=m['concurrency'],independent_decisions_verified=independent,
           wall_seconds=(max(b for a,b in times)-min(a for a,b in times)).total_seconds(),
           methods=stats(rows),by_stratum={v:stats([r for r in rows if r['stratum']==v]) for v in ('primary','control')},
           by_rep={str(rep):stats([r for r in rows if r['rep']==rep]) for rep in (1,2)},
           by_block={block:stats([r for r in rows if r['block_id']==block]) for block in sorted({r['block_id'] for r in rows})},
           status_counts={role:{status:sum(r['role']==role and r['status']==status for r in rows) for status in sorted(TERMINAL)} for role in ROLES},
           stage_cost=cost,rows=rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','collect','mock','replay']);p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--concurrency',type=int,default=4)
    a=p.parse_args()
    if a.action=='prepare':prepare(a.run_dir,a.concurrency)
    elif a.action=='collect':collect(a.run_dir)
    elif a.action=='mock':
        prepare(a.run_dir,a.concurrency,mode='MOCK')
        with NetworkBlocker():collect(a.run_dir)
    else:
        with NetworkBlocker():result=replay(a.run_dir)
        if read(a.run_dir/'summary.json')!=result:raise ValueError('saved summary differs from replay')
        write(a.run_dir/'audit.json',dict(status='PASS_OFFLINE_REPLAY',independent_decisions=result['independent_decisions_verified'],scope=result['scope']))
        write(a.run_dir/'delivery_integrity.json',{str(f.relative_to(a.run_dir)):digest(f) for f in sorted(a.run_dir.rglob('*')) if f.is_file() and f.name!='delivery_integrity.json'})
        print({k:v for k,v in result.items() if k not in ('rows','by_block')})

if __name__=='__main__':main()
