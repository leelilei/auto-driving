"""Frozen Scene-Pilot12 collector/replay. Preparation never authorizes model calls."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import threading

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.scene_policy import Policy, parse_response, request, execute, evaluate
from src.llm_client import LLM, load_config
from scripts.experiment import NetworkBlocker

DATA=ROOT/'data/scene_pilot12_candidate'
ROLES=('direct','language','evidence')
TERMINAL={'COMPLETE','SCHEMA_FAILED','UPSTREAM_SCHEMA_FAILED'}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,value):
    temp=p.with_suffix(p.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.replace(p)
def now():return datetime.now(timezone.utc).isoformat()

def prepare(run,config_path=None,development_authorization=None):
    if run.exists():raise ValueError('refuse to overwrite snapshot')
    run.mkdir(parents=True)
    for name in ('model_inputs.json','gold_and_traces.json','author_review_cases.json'):
        shutil.copyfile(DATA/name,run/name)
    public=read(run/'model_inputs.json')
    if len(public)!=12 or len({x['case_id'] for x in public})!=12:raise ValueError('expected twelve unique cases')
    plan=[dict(call_id=f"{c['case_id']}__r{rep}__{role}",case_id=c['case_id'],rep=rep,role=role)
          for rep in (1,2) for c in public for role in ROLES]
    write(run/'plan.json',plan)
    config=read(config_path or ROOT/'configs/v5/deepseek_official_v41_flash_preview.json')
    config.update(timeout=120,max_output_tokens=1600,retries=0,max_concurrency=1)
    write(run/'config.json',config)
    files=['model_inputs.json','gold_and_traces.json','author_review_cases.json','plan.json','config.json']
    if development_authorization:
        write(run/'development_authorization.json',dict(user_statement=development_authorization,
              scope='UNREVIEWED_DEVELOPMENT_ONLY',human_review='PENDING'))
        files.append('development_authorization.json')
    source=[Path(__file__),ROOT/'src/scene_policy.py',ROOT/'src/llm_client.py']
    write(run/'manifest.json',dict(protocol='scene-pilot12-engineering-2-json-wrapper',created=now(),stage='PREPARED_NOT_ADMITTED',
          scope='development_only',model=config['model'],model_identity_status='candidate_requires_live_check_before_formal_use',
          planned=72,repetitions=2,concurrency=4,max_transport_recoveries=8,max_attempts_per_unit=2,
          files={f:digest(run/f) for f in files},sources={str(p.relative_to(ROOT)):digest(p) for p in source}))
    write(run/'admission_template.json',dict(status='PENDING',reviewer=None,reviewed_at=None,source_user_statement=None,
          reviewed_case_ids=[],public_sha256=digest(run/'model_inputs.json'),gold_sha256=digest(run/'gold_and_traces.json'),
          approved_model=None,max_physical_attempts=80,note='Do not infer human semantic approval from a generic instruction to proceed.'))
    print('Prepared 72 logical units; human review pending; no API calls')

def verify(run):
    manifest=read(run/'manifest.json')
    for f,h in manifest['files'].items():
        if digest(run/f)!=h:raise ValueError(f'changed snapshot: {f}')
    for f,h in manifest['sources'].items():
        if digest(ROOT/f)!=h:raise ValueError(f'changed source: {f}')
    return manifest

def check_admission(run,path):
    verify(run)
    if path is None or not path.exists():raise ValueError('human semantic review attestation is missing')
    a=read(path)
    ids={x['case_id'] for x in read(run/'model_inputs.json')}
    if a.get('status')!='APPROVED' or not all(isinstance(a.get(k),str) and a[k].strip() for k in ('reviewer','reviewed_at','source_user_statement')):
        raise ValueError('human semantic review is not approved')
    if set(a.get('reviewed_case_ids',[]))!=ids:raise ValueError('human review does not cover the frozen twelve cases')
    for file,key in [('model_inputs.json','public_sha256'),('gold_and_traces.json','gold_sha256')]:
        if digest(run/file)!=a.get(key):raise ValueError('review refers to a different dataset version')
    if a.get('approved_model')!=read(run/'config.json')['model']:raise ValueError('model identity not admitted')
    if a.get('max_physical_attempts')!=80:raise ValueError('expected 72 base plus at most eight transport recoveries')

def records_for(run,call_id):
    return [read(p) for p in sorted((run/'attempts').glob(call_id+'.a*.json'))]

def resolve(run,call_id):
    records=records_for(run,call_id)
    terminal=[r for r in records if r['status'] in TERMINAL]
    if len(terminal)>1:raise ValueError('multiple terminal answers for one logical unit')
    return terminal[0] if terminal else records[-1] if records else None

def replay(run,save=True):
    verify(run)
    plan=read(run/'plan.json'); expected={j['call_id'] for j in plan}
    kind=read(run/'run_kind.json')['kind']
    if kind not in ('MOCK','REAL','UNREVIEWED_DEVELOPMENT'):raise ValueError('unknown run kind')
    if kind=='REAL':check_admission(run,run/'admission.json')
    if kind=='UNREVIEWED_DEVELOPMENT':check_development(run)
    physical=[read(p) for p in (run/'attempts').glob('*.json')]
    if any(r.get('call_id') not in expected for r in physical):raise ValueError('unknown ledger unit')
    if any(r.get('source')!=kind for r in physical):raise ValueError('mixed record provenance')
    recoveries=0
    for j in plan:
        records=records_for(run,j['call_id'])
        paths=sorted((run/'attempts').glob(j['call_id']+'.a*.json'))
        if len(records)>2:raise ValueError('attempt budget exceeded')
        for i,(path,r) in enumerate(zip(paths,records),1):
            if path.name!=f"{j['call_id']}.a{i}.json" or r['role']!=j['role'] or r['call_id']!=j['call_id']:
                raise ValueError('invalid attempt identity or sequence')
            if i>1 and records[i-2]['status']!='TRANSPORT_FAILED':raise ValueError('only transport failures may retry')
        recoveries+=max(0,len(records)-1)
    if recoveries>8:raise ValueError('recovery budget exceeded')
    resolved={cid:resolve(run,cid) for cid in expected}
    if not all(r and r['status'] in TERMINAL for r in resolved.values()):raise ValueError('incomplete ledger; no method ranking permitted')
    public={c['case_id']:c for c in read(run/'model_inputs.json')}
    gold={c['case_id']:c for c in read(run/'gold_and_traces.json')}
    pairs={c['case_id']:c['pair_id'] for c in read(run/'author_review_cases.json')}
    parsed={}
    # Reparse originals, not the saved claimed parsed fields.
    for j in plan:
        r=resolved[j['call_id']]
        if r['status']=='COMPLETE':
            policy,_=parse_response(r['raw_response'])
            if policy.to_dict()!=r['parsed_policy']:raise ValueError('parsed policy does not match raw response')
            parsed[j['call_id']]=policy
        elif r['status']=='SCHEMA_FAILED':
            try:parse_response(r['raw_response'])
            except (ValueError,TypeError):pass
            else:raise ValueError('schema failure record contains valid output')
    rows=[]
    for j in plan:
        cid=j['case_id'];r=resolved[j['call_id']];direct=parsed.get(f"{cid}__r{j['rep']}__direct")
        if r['status']=='UPSTREAM_SCHEMA_FAILED':
            if j['role']=='direct' or direct is not None:raise ValueError('invalid upstream skip')
            if resolved[f"{cid}__r{j['rep']}__direct"]['status']!='SCHEMA_FAILED':raise ValueError('skip not caused by direct schema failure')
        else:
            expected_request=request(public[cid],j['role'],direct if j['role']!='direct' else None)
            if any(a.get('request')!=expected_request for a in records_for(run,j['call_id'])):
                raise ValueError('recorded request differs from frozen inputs/prompt')
        raw=parsed.get(j['call_id']);effective=raw if raw is not None else direct if j['role']!='direct' else None
        decision=execute(public[cid]['scene'],effective) if effective else None
        scored=evaluate(effective,decision,gold[cid]);base=evaluate(direct,execute(public[cid]['scene'],direct) if direct else None,gold[cid])
        rows.append(dict(**j,pair_id=pairs[cid],gold_status=gold[cid]['status'],status=r['status'],policy=effective.to_dict() if effective else None,
                         decision=decision,raw_rule_correct=raw is not None and raw.to_dict()==gold[cid]['policy'],
                         fallback=j['role']!='direct' and raw is None and direct is not None,
                         corrected=not base['object_success'] and scored['object_success'],
                         damaged=base['object_success'] and not scored['object_success'],**scored))
    roles={role:{'n':24,**{k:sum(r[k] for r in rows if r['role']==role) for k in
           ('rule_correct','raw_rule_correct','object_success','feasible_success','false_infeasible','fallback','corrected','damaged')}} for role in ROLES}
    physical_calls=[r for r in physical if r['status']!='UPSTREAM_SCHEMA_FAILED']
    cost={}
    for role in ROLES:
        relevant=[r for r in physical_calls if r['role']==role]
        latencies=[r['telemetry']['latency_seconds'] for r in relevant if (r.get('telemetry') or {}).get('latency_seconds') is not None]
        cost[role]={'physical_calls':len(relevant),'known_provider_tokens':sum((r.get('telemetry') or {}).get('total_tokens',0) for r in relevant if (r.get('telemetry') or {}).get('usage_source')=='provider'),
                    'usage_unknown_calls':sum((r.get('telemetry') or {}).get('usage_source')!='provider' for r in relevant),
                    'latency_observed_calls':len(latencies),'sum_request_seconds':sum(latencies),
                    'median_request_seconds':statistics.median(latencies) if latencies else None}
    # Reviews share Direct in research; deployment cost includes their own Direct stage.
    deployment={role:cost[role]['known_provider_tokens']+(cost['direct']['known_provider_tokens'] if role!='direct' else 0) for role in ROLES}
    pair_results=[dict(role=role,rep=rep,pair_id=pair,
         both_correct=all(r['object_success'] for r in rows if r['role']==role and r['rep']==rep and r['pair_id']==pair))
         for role in ROLES for rep in (1,2) for pair in sorted(set(pairs.values()))]
    result=dict(collection_complete=True,scope={'MOCK':'MOCK_ENGINEERING_ONLY','REAL':'DEVELOPMENT_MODEL_RUN','UNREVIEWED_DEVELOPMENT':'UNREVIEWED_DEVELOPMENT_ONLY'}[kind],
           logical_units=72,physical_calls=len(physical_calls),methods=roles,stage_cost=cost,deployment_known_tokens=deployment,
           status_counts={role:{status:sum(r['role']==role and r['status']==status for r in rows) for status in sorted(TERMINAL)} for role in ROLES},
           by_rep={rep:{role:sum(r['object_success'] for r in rows if r['rep']==rep and r['role']==role) for role in ROLES} for rep in (1,2)},
           by_gold_status={status:{role:{'n':sum(r['role']==role and r['gold_status']==status for r in rows),
               'object_success':sum(r['object_success'] for r in rows if r['role']==role and r['gold_status']==status)} for role in ROLES} for status in ('OK','INFEASIBLE')},
           pair_results=pair_results,rows=rows)
    if save:write(run/'summary.json',result)
    return result

def check_development(run):
    manifest=verify(run)
    if 'development_authorization.json' not in manifest['files']:raise ValueError('development authorization not frozen')
    a=read(run/'development_authorization.json')
    if a.get('scope')!='UNREVIEWED_DEVELOPMENT_ONLY' or not a.get('user_statement'):
        raise ValueError('missing development run authorization')

def collect(run,admission=None,mock=False,development=False):
    verify(run)
    if mock and development:raise ValueError('mock cannot be development model run')
    if development:check_development(run)
    elif not mock:check_admission(run,admission)
    kind='MOCK' if mock else 'UNREVIEWED_DEVELOPMENT' if development else 'REAL'
    if (run/'run_kind.json').exists() and read(run/'run_kind.json')['kind']!=kind:raise ValueError('mock and real runs cannot mix')
    write(run/'run_kind.json',dict(kind=kind));(run/'attempts').mkdir(exist_ok=True)
    if not mock and not development:
        # Copy the exact authorization evidence into the run; never synthesize approval.
        if (run/'admission.json').exists() and digest(run/'admission.json')!=digest(admission):raise ValueError('admission changed')
        if not (run/'admission.json').exists():shutil.copyfile(admission,run/'admission.json')
    if not mock:
        env_name=read(run/'config.json')['api_key_env']
        if not os.environ.get(env_name):
            key=subprocess.run(['security','find-generic-password','-s',env_name,'-w'],capture_output=True,text=True,check=True)
            os.environ[env_name]=key.stdout.strip()
    config=load_config(run/'config.json');public=read(run/'model_inputs.json')
    stop=threading.Event();lock=threading.Lock()
    recoveries=len(list((run/'attempts').glob('*.a2.json')))
    def call(cid,rep,role,payload):
        nonlocal recoveries
        call_id=f'{cid}__r{rep}__{role}';old=resolve(run,call_id)
        if old and old['status'] in TERMINAL:return old
        for attempt in (1,2):
            path=run/'attempts'/f'{call_id}.a{attempt}.json'
            if path.exists():
                existing=read(path)
                if existing['status']=='STARTED':raise ValueError('unresolved started request; billing/response reconciliation required')
                if existing['status'] in TERMINAL:return existing
                continue
            if attempt==2:
                with lock:
                    if recoveries>=8:return old
                    recoveries+=1
            record=dict(call_id=call_id,role=role,request=payload,started=now(),status='STARTED',source=kind)
            write(path,record)
            llm=None
            try:
                if mock:
                    # Deliberately fixed dummy response, never reads gold. No model performance claim.
                    raw=json.dumps(dict(selection='nearest_from_bank',availability_reference='arrival',return_by=None,evidence={}))
                    telemetry={'usage_source':'mock','total_tokens':0,'success':True}
                else:
                    llm=LLM(config);raw=llm.complete(**payload);telemetry=llm.telemetry[-1]
                    if getattr(llm.client,'last_response',None) is not None:
                        record['provider_response']=llm.client.last_response
                record['raw_response']=raw;record['telemetry']=telemetry
                policy,evidence=parse_response(raw)
                record.update(status='COMPLETE',parsed_policy=policy.to_dict(),evidence=evidence)
            except Exception as exc:
                if llm and llm.telemetry:record['telemetry']=llm.telemetry[-1]
                record.update(status='SCHEMA_FAILED' if 'raw_response' in record else 'TRANSPORT_FAILED',error_type=type(exc).__name__,error_message=str(exc))
            record['finished']=now();write(path,record)
            if record['status'] in TERMINAL:return record
            if any(code in record.get('error_message','') for code in ('401','403','429')):stop.set();return record
            old=record
        return old
    def unit(item,rep):
        if stop.is_set():return
        cid=item['case_id'];r=call(cid,rep,'direct',request(item,'direct'))
        if not r or r['status']=='TRANSPORT_FAILED':stop.set();return
        if r['status']=='SCHEMA_FAILED':
            for role in ('language','evidence'):
                call_id=f'{cid}__r{rep}__{role}';path=run/'attempts'/f'{call_id}.a1.json'
                if not path.exists():write(path,dict(call_id=call_id,role=role,status='UPSTREAM_SCHEMA_FAILED',source=kind,telemetry=None))
            return
        candidate=Policy.parse(r['parsed_policy'])
        for role in (('language','evidence') if rep==1 else ('evidence','language')):
            rr=call(cid,rep,role,request(item,role,candidate))
            if not rr or rr['status']=='TRANSPORT_FAILED':stop.set();return
    # One complete real unit verifies the chain before parallel work.
    unit(public[0],1)
    if not stop.is_set():
        tasks=[(item,rep) for rep in (1,2) for item in public if not (rep==1 and item['case_id']==public[0]['case_id'])]
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(unit,*args) for args in tasks]
            for i,f in enumerate(futures,1):f.result();print(f'Unit {i+1}/24 processed',flush=True)
    if stop.is_set():
        write(run/'collection_status.json',dict(collection_complete=False,status='INCOMPLETE_TRANSPORT',scope=kind))
        raise RuntimeError('collection incomplete after transport failures; inspect ledger before resuming')
    result=replay(run)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','collect','mock','replay']);p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--admission',type=Path)
    args=p.parse_args()
    if args.action=='prepare':prepare(args.run_dir)
    elif args.action=='replay':
        with NetworkBlocker():result=replay(args.run_dir)
        print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    elif args.action=='mock':
        with NetworkBlocker():collect(args.run_dir,mock=True)
    else:collect(args.run_dir,args.admission)

if __name__=='__main__':main()
