"""Frozen 60-call glossary-only review control, matched to existing Direct candidates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import scene_rule30_run as base
from src.scene_policy import Policy,parse_response,execute,evaluate
from src.llm_client import LLM,load_config

REFERENCE=ROOT/'results/scene_rule30/20260910T152533Z_haiku_c16_development'
GLOSSARY='''
Definitions of the three selection values:
- nearest_from_bank: minimize the straight-line distance d(B, P) from bank B to the pharmacy P among eligible pharmacies.
- minimum_added_distance: minimize d(B, P) + d(P, H) - d(B, H) among eligible pharmacies, where H is home.
- highest_rating: maximize the pharmacy rating among eligible pharmacies.
These definitions specify the selection field. Read which objective is requested from the instruction; the availability_reference and return_by fields retain their definitions above.
'''
TERMINAL={'COMPLETE','SCHEMA_FAILED'}

def glossary_request(original):
    # Exact original language-review user message; no gold or computed evidence input.
    return dict(system=original['system']+GLOSSARY,user=original['user'])

def prepare(run,mode='REAL'):
    if run.exists():raise ValueError('refuse overwrite')
    with base.NetworkBlocker():
        baseline=base.replay(REFERENCE)
        assert baseline==base.read(REFERENCE/'summary.json')
    run.mkdir(parents=True);(run/'attempts').mkdir()
    for name in ('model_inputs.json','author_review_cases.json','gold_and_traces.json','config.json'):
        shutil.copyfile(REFERENCE/name,run/name)
    base.write(run/'reference_summary.json',baseline)
    plan=[];reference_records={}
    for j in base.read(REFERENCE/'run_plan.json'):
        if j['role']!='language':continue
        cid=j['case_id'];rep=j['rep'];direct=base.latest(REFERENCE,f'{cid}__r{rep}__direct')
        original=base.latest(REFERENCE,j['call_id'])
        assert direct['status']=='COMPLETE'
        assert json.loads(original['request']['user'])['candidate_policy']==direct['parsed_policy']
        reference_records[j['call_id']]=original
        reference_records[direct['call_id']]=direct
        plan.append(dict(call_id=f'{cid}__r{rep}__glossary',case_id=cid,rep=rep,
                         direct_policy=direct['parsed_policy'],request=glossary_request(original['request'])))
    base.write(run/'plan.json',plan);base.write(run/'reference_records.json',reference_records)
    (run/'glossary.txt').write_text(GLOSSARY)
    files={f.name:base.digest(f) for f in run.iterdir() if f.is_file()}
    sources={}
    for name in ('scripts/scene_rule30_glossary.py','scripts/scene_rule30_run.py','scripts/scene_pilot12.py',
                 'scripts/scene_haiku_contract.py','scripts/prepare_scene_pilot12.py','src/scene_policy.py','src/llm_client.py'):
        target=run/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        sources[name]=base.digest(target)
    base.write(run/'manifest.json',dict(created=base.now(),scope='UNREVIEWED_DEVELOPMENT_CONTROL',mode=mode,
        human_review='PENDING',authorization='用户同意推进60次明确术语定义的语言复核对照。',reference=str(REFERENCE),
        reference_manifest_sha256=base.digest(REFERENCE/'manifest.json'),planned=60,initial_concurrency=8,
        failure_concurrency=4,max_recoveries=6,max_attempts_per_unit=2,files=files,sources=sources,
        stopping='Stop 401/403/429; reduce to4 on other transport failures; retry failed transport once, max6. Never retry schema/semantic failures.',
        limitation='Added development arm in a later time window; reference methods are not contemporaneously resampled.'))
    verify(run)

def verify(run):
    m=base.read(run/'manifest.json')
    for f,h in m['files'].items():
        if base.digest(run/f)!=h:raise ValueError('frozen input changed: '+f)
    for f,h in m['sources'].items():
        if base.digest(ROOT/f)!=h or base.digest(run/'source'/f)!=h:raise ValueError('source changed: '+f)
    plan=base.read(run/'plan.json');refs=base.read(run/'reference_records.json')
    if len(plan)!=60 or len({j['call_id'] for j in plan})!=60:raise ValueError('expected 60 unique jobs')
    for j in plan:
        old=refs[f"{j['case_id']}__r{j['rep']}__language"]
        direct=refs[f"{j['case_id']}__r{j['rep']}__direct"]
        if j['request']!=glossary_request(old['request']) or j['direct_policy']!=direct['parsed_policy']:
            raise ValueError('candidate or prompt mismatch')
        p,_=parse_response(direct['raw_response'])
        if p.to_dict()!=j['direct_policy']:raise ValueError('source candidate parse mismatch')
        user=json.loads(j['request']['user'])
        if user['computed_scene_facts'] is not None:raise ValueError('computed facts leaked into control')
    return m

def attempts(run,cid):return [base.read(f) for f in sorted((run/'attempts').glob(cid+'.a*.json'))]

def collect(run):
    m=verify(run);config=load_config(run/'config.json');real=m['mode']=='REAL'
    if real and not os.environ.get(config.api_key_env):
        k=subprocess.run(['security','find-generic-password','-s',config.api_key_env,'-w'],capture_output=True,text=True,check=True)
        os.environ[config.api_key_env]=k.stdout.strip()
    def call(j,attempt,concurrency):
        record=dict(call_id=j['call_id'],source=m['mode'],request=j['request'],started=base.now(),status='STARTED',concurrency=concurrency)
        path=run/'attempts'/f"{j['call_id']}.a{attempt}.json";base.write(path,record);client=None
        try:
            if real:
                client=LLM(config);raw=client.complete(**j['request'])
                record.update(provider_response=client.client.last_response,telemetry=client.telemetry[-1])
            else:
                raw=json.dumps(dict(selection='nearest_from_bank',availability_reference='arrival',return_by=None,evidence={}))
                record['telemetry']={'latency_seconds':0,'usage_source':'mock'}
            record['raw_response']=raw;policy,_=parse_response(raw)
            record.update(status='COMPLETE',parsed_policy=policy.to_dict())
        except Exception as e:
            message=str(e);key=os.environ.get(config.api_key_env)
            if key:message=message.replace(key,'[REDACTED]')
            record.update(status='SCHEMA_FAILED' if 'raw_response' in record else 'TRANSPORT_FAILED',error=message)
            if client and client.telemetry:record['telemetry']=client.telemetry[-1]
        record['finished']=base.now();base.write(path,record);return record
    pending=[];retry_count=0
    for j in base.read(run/'plan.json'):
        rs=attempts(run,j['call_id']);retry_count+=max(0,len(rs)-1)
        if any(r['status']=='STARTED' for r in rs):raise ValueError('unreconciled STARTED')
        if not rs or rs[-1]['status'] not in TERMINAL:pending.append(j)
    concurrency=m['initial_concurrency'];first=True
    while pending:
        batch=pending[:1 if first else concurrency];pending=pending[len(batch):];first=False
        jobs=[]
        for j in batch:
            a=len(attempts(run,j['call_id']))+1
            if a>2:raise RuntimeError('transport attempts exhausted; incomplete')
            if a==2:
                if retry_count>=m['max_recoveries']:raise RuntimeError('recovery budget exhausted; incomplete')
                retry_count+=1
            jobs.append((j,a,concurrency))
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            outcomes=list(pool.map(lambda args:call(*args),jobs))
        failed=[]
        for j,out in zip(batch,outcomes):
            if out['status']=='TRANSPORT_FAILED':
                if any(f'HTTP {c}' in out.get('error','') for c in (401,403,429)):raise RuntimeError('provider refused request; incomplete')
                failed.append(j)
        if failed:
            concurrency=m['failure_concurrency'];pending=failed+pending
        print(f"Remaining logical jobs: {len(pending)}; concurrency: {concurrency}",flush=True)
    result=replay(run);base.write(run/'summary.json',result)
    print(result['glossary'],flush=True)

def replay(run):
    m=verify(run);plan=base.read(run/'plan.json');byid={j['call_id']:j for j in plan}
    physical=[(f,base.read(f)) for f in (run/'attempts').glob('*.json')]
    for f,r in physical:
        if r.get('call_id') not in byid or r.get('source')!=m['mode'] or f.name not in [r['call_id']+f'.a{i}.json' for i in (1,2)]:raise ValueError('unexpected ledger record')
    public={c['case_id']:c for c in base.read(run/'model_inputs.json')}
    gold={c['case_id']:c for c in base.read(run/'gold_and_traces.json')}
    old=base.read(run/'reference_summary.json');oldrows={r['call_id']:r for r in old['rows']}
    rows=[];retries=0
    for j in plan:
        rs=attempts(run,j['call_id']);retries+=max(0,len(rs)-1)
        if not 1<=len(rs)<=2 or rs[-1]['status'] not in TERMINAL:raise ValueError('incomplete unit')
        paths=sorted((run/'attempts').glob(j['call_id']+'.a*.json'))
        if any(p.name!=j['call_id']+f'.a{i}.json' for i,p in enumerate(paths,1)):raise ValueError('missing attempt sequence')
        for i,a in enumerate(rs):
            if a['request']!=j['request']:raise ValueError('changed request')
            if i<len(rs)-1 and a['status']!='TRANSPORT_FAILED':raise ValueError('illegal retry')
        r=rs[-1];policy=None
        if r['status']=='COMPLETE':
            policy,_=parse_response(r['raw_response'])
            if policy.to_dict()!=r['parsed_policy']:raise ValueError('parse mismatch')
        else:
            try:parse_response(r['raw_response'])
            except (ValueError,TypeError):pass
            else:raise ValueError('valid output labelled failure')
        direct=Policy.parse(j['direct_policy']);effective=policy or direct;scene=public[j['case_id']]['scene'];g=gold[j['case_id']]
        d=execute(scene,effective);ref=base.solve(scene,effective.to_dict())
        if d!=dict(status=ref['status'],selected_poi_ids=sorted(ref['accepted_poi_ids'])):raise ValueError('independent execution mismatch')
        score=evaluate(effective,d,g);prior=oldrows[f"{j['case_id']}__r{j['rep']}__direct"]
        rows.append(dict(call_id=j['call_id'],case_id=j['case_id'],rep=j['rep'],block_id=prior['block_id'],stratum=prior['stratum'],
            status=r['status'],policy=effective.to_dict(),decision=d,fallback=policy is None,
            raw_rule_correct=policy is not None and policy.to_dict()==g['policy'],
            raw_object_success=policy is not None and score['object_success'],
            corrected=not prior['object_success'] and score['object_success'],damaged=prior['object_success'] and not score['object_success'],**score))
    if retries>m['max_recoveries']:raise ValueError('recovery budget exceeded')
    def stats(rs):
        fields=('rule_correct','raw_rule_correct','object_success','raw_object_success','corrected','damaged','fallback')
        return dict(n=len(rs),**{k:sum(r[k] for r in rs) for k in fields})
    comparisons={}
    for role in base.ROLES:
        pairs=[(r,oldrows[f"{r['case_id']}__r{r['rep']}__{role}"]) for r in rows]
        comparisons[role]=dict(glossary_only_correct=sum(a['object_success'] and not b['object_success'] for a,b in pairs),
            reference_only_correct=sum(b['object_success'] and not a['object_success'] for a,b in pairs))
    us=[r['provider_response']['usage'] for f,r in physical if (r.get('provider_response') or {}).get('usage') is not None]
    sums={k:sum(u.get(k,0) for u in us) for k in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')}
    ls=[r['telemetry']['latency_seconds'] for f,r in physical if r.get('telemetry')]
    return dict(scope=m['scope'] if m['mode']=='REAL' else 'MOCK_ENGINEERING_ONLY',human_review='PENDING',complete=True,
        physical_calls=len(physical),logical_units=60,retries=retries,glossary=stats(rows),reference_methods=old['methods'],
        by_stratum={v:stats([r for r in rows if r['stratum']==v]) for v in ('primary','control')},
        by_rep={str(rep):stats([r for r in rows if r['rep']==rep]) for rep in (1,2)},comparisons=comparisons,
        cost=dict(**sums,token_components_sum=sum(sums.values()),usage_unknown=len(physical)-len(us),median_seconds=statistics.median(ls)),rows=rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['run','replay','mock']);p.add_argument('--run-dir',type=Path)
    a=p.parse_args()
    if a.action in ('run','mock'):
        run=a.run_dir or ROOT/'results/scene_rule30'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_haiku_glossary60')
        prepare(run,mode='MOCK' if a.action=='mock' else 'REAL');print('RUN_DIR='+str(run),flush=True)
        if a.action=='mock':
            with base.NetworkBlocker():collect(run)
        else:collect(run)
    else:
        if a.run_dir is None:raise ValueError('run directory required')
        with base.NetworkBlocker():result=replay(a.run_dir)
        if result!=base.read(a.run_dir/'summary.json'):raise ValueError('summary replay differs')
        base.write(a.run_dir/'audit.json',dict(status='PASS_OFFLINE_REPLAY',independent_decisions=60,matched_candidates=60))
        base.write(a.run_dir/'delivery_integrity.json',{str(f.relative_to(a.run_dir)):base.digest(f) for f in sorted(a.run_dir.rglob('*')) if f.is_file() and f.name!='delivery_integrity.json'})
        print({k:v for k,v in result.items() if k!='rows'})

if __name__=='__main__':main()
