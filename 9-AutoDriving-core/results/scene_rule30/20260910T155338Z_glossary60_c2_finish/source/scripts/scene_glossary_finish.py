"""Bounded c2 continuation of the same glossary experiment; no valid answer resampling."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts import scene_rule30_glossary as g
from scripts.scene_glossary_http1 import CurlLLM
from src.llm_client import load_config
from src.scene_policy import parse_response

def main():
    parent=Path(sys.argv[1]);g.verify(parent)
    run=ROOT/'results/scene_rule30'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_glossary60_c2_finish')
    g.prepare(run);shutil.copytree(parent,run/'parent_partial')
    inherited={}
    for j in g.base.read(parent/'plan.json'):
        rs=g.attempts(parent,j['call_id'])
        if rs and rs[-1]['status'] in g.TERMINAL:
            assert len(rs)==1
            name=j['call_id']+'.a1.json';shutil.copyfile(parent/'attempts'/name,run/'attempts'/name)
            inherited[name]=g.base.digest(run/'attempts'/name)
    previous_failures=sum(g.base.read(p)['status']=='TRANSPORT_FAILED' for p in (parent/'attempts').glob('*.json'))
    previous_failures+=g.base.read(parent/'continuation.json')['parent_transport_failures']
    assert previous_failures==6
    config=g.base.read(run/'config.json');config['transport']='curl_http1';g.base.write(run/'config.json',config)
    g.base.write(run/'continuation.json',dict(parent=str(parent),inherited_answers=inherited,previous_transport_failures=previous_failures,
         combined_budget=72,reason='Same task over HTTP/1.1 c2 after transient TLS failures; delay retries to later batches. Valid answers remain unchanged.',
         diagnostic='HEAD / returned200; xcode resolved to198.18.0.149 via utun0. Root cause not determined.'))
    m=g.base.read(run/'manifest.json');m.update(initial_concurrency=2,failure_concurrency=2,max_recoveries=6,
          combined_request_budget=72,transport_revision='Documented bounded c2 recovery; no semantic changes')
    for f in [run/'config.json',run/'continuation.json',*list((run/'parent_partial').rglob('*'))]:
        if f.is_file():m['files'][str(f.relative_to(run))]=g.base.digest(f)
    for name in ('scripts/scene_glossary_http1.py','scripts/scene_glossary_finish.py'):
        shutil.copyfile(ROOT/name,run/'source'/name);m['sources'][name]=g.base.digest(ROOT/name)
    g.base.write(run/'manifest.json',m);g.verify(run)
    cfg=load_config(run/'config.json')
    if not os.environ.get(cfg.api_key_env):
        r=subprocess.run(['security','find-generic-password','-s',cfg.api_key_env,'-w'],capture_output=True,text=True,check=True)
        os.environ[cfg.api_key_env]=r.stdout.strip()
    def call(j):
        seq=len(g.attempts(run,j['call_id']))+1
        r=dict(call_id=j['call_id'],source='REAL',request=j['request'],started=g.base.now(),status='STARTED',concurrency=2)
        path=run/'attempts'/f"{j['call_id']}.a{seq}.json";g.base.write(path,r);llm=CurlLLM(cfg)
        try:
            raw=llm.complete(**j['request']);r.update(raw_response=raw,provider_response=llm.client.last_response)
            policy,_=parse_response(raw);r.update(status='COMPLETE',parsed_policy=policy.to_dict())
        except Exception as e:r.update(status='SCHEMA_FAILED' if 'raw_response' in r else 'TRANSPORT_FAILED',error_type=type(e).__name__,error=str(e).replace(os.environ[cfg.api_key_env],'[REDACTED]'))
        r.update(finished=g.base.now(),telemetry=llm.telemetry[-1] if llm.telemetry else None)
        g.base.write(path,r);return r
    pending=[j for j in g.base.read(run/'plan.json') if not g.attempts(run,j['call_id'])]
    recoveries=0;exhausted=[]
    print('RUN_DIR='+str(run),flush=True)
    while pending:
        batch=pending[:2];pending=pending[2:]
        for j in batch:
            if g.attempts(run,j['call_id']):
                recoveries+=1
                if recoveries>6:raise RuntimeError('combined budget exhausted')
        with ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(call,batch))
        for j,r in zip(batch,out):
            if r['status']=='TRANSPORT_FAILED':
                if any(f'HTTP {c}' in r.get('error','') for c in (401,403,429)):raise RuntimeError('provider refusal; stop')
                if len(g.attempts(run,j['call_id']))<2:pending.append(j)
                else:exhausted.append(j['call_id'])
        print(f'Remaining {len(pending)}, exhausted {len(exhausted)}',flush=True)
        if pending:time.sleep(1)
    if exhausted:raise RuntimeError('Unresolved transport failures remain')
    with g.base.NetworkBlocker():result=g.replay(run)
    g.base.write(run/'summary.json',result)
    total=result['physical_calls']+previous_failures
    assert total<=72
    g.base.write(run/'audit.json',dict(status='PASS_OFFLINE_MATCHED_CONTROL',independent_decisions=60,combined_physical_calls=total,
       inherited_answers=len(inherited),human_review='PENDING'))
    g.base.write(run/'delivery_integrity.json',{str(f.relative_to(run)):g.base.digest(f) for f in sorted(run.rglob('*')) if f.is_file() and f.name!='delivery_integrity.json'})
    print(result['glossary'],flush=True)

if __name__=='__main__':main()
