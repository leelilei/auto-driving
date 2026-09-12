"""Bounded Anthropic Messages concurrency probe and separate development smoke."""
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.scene_pilot12 import write, read, digest
from src.scene_policy import request, parse_response, execute, evaluate

MODEL='claude-haiku-4-5-20251001'

def main():
    base=os.environ['ANTHROPIC_BASE_URL'].rstrip('/')
    token=os.environ['ANTHROPIC_AUTH_TOKEN']
    run=ROOT/'results/scene_pilot12'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_haiku_fhl_probe')
    run.mkdir(parents=True,exist_ok=False)
    public=read(ROOT/'data/scene_pilot12_candidate/model_inputs.json')[:2]
    gold=read(ROOT/'data/scene_pilot12_candidate/gold_and_traces.json')[:2]
    write(run/'public.json',public);write(run/'gold.json',gold)
    write(run/'manifest.json',dict(model=MODEL,base_url=base,wire_api='anthropic_messages',
        levels=[1,2,4,6,8],waves=2,retries=0,timeout=60,temperature=0,
        probe_max_tokens=64,scene_max_tokens=1600,max_total_requests=56,
        human_review='PENDING',scope='NODE_PROBE_AND_UNREVIEWED_DEVELOPMENT_SMOKE',
        stopping='Stop increasing on any failed wave; validate last passing level (max4) with scene prompt, then six sequential scene calls.',
        source_sha256=digest(Path(__file__)),policy_sha256=digest(ROOT/'src/scene_policy.py')))
    print('RUN_DIR='+str(run),flush=True)

    def call(cid,prompt,max_tokens,expected=None):
        payload=dict(model=MODEL,max_tokens=max_tokens,temperature=0,system=prompt['system'],
                     messages=[dict(role='user',content=prompt['user'])])
        record=dict(call_id=cid,status='STARTED',request=payload)
        path=run/(cid+'.json');write(path,record)
        started=time.perf_counter()
        req=urllib.request.Request(base+'/v1/messages',data=json.dumps(payload).encode(),
            headers={'Content-Type':'application/json','x-api-key':token,'Authorization':'Bearer '+token,'anthropic-version':'2023-06-01'})
        try:
            with urllib.request.urlopen(req,timeout=60) as res:
                record['http_status']=res.status;data=json.load(res)
            record['response']=data
            raw=''.join(b.get('text','') for b in data.get('content',[]) if b.get('type')=='text')
            record['raw_response']=raw
            if expected is not None:
                if json.loads(raw)!=expected:raise ValueError('unexpected probe JSON')
            else:
                policy,_=parse_response(raw);record['policy']=policy.to_dict()
            record['status']='PASS'
        except urllib.error.HTTPError as e:
            record.update(status='HTTP_FAILED',http_status=e.code,
                          error=e.read(500).decode(errors='replace').replace(token,'[REDACTED]'))
        except Exception as e:
            record.update(status='SCHEMA_FAILED' if 'response' in record else 'TRANSPORT_FAILED',
                          error_type=type(e).__name__,error=str(e).replace(token,'[REDACTED]'))
        record['latency_seconds']=round(time.perf_counter()-started,3);write(path,record)
        return record

    def wave(level,idx,scene=False):
        start=time.perf_counter()
        def one(i):
            expected={'ok':True,'id':i}
            prompt=request(public[0],'direct') if scene else {'system':'Return exactly the requested JSON. No markdown.',
                                                            'user':json.dumps(expected)}
            return call(f"{'scene_load' if scene else 'probe'}_c{level}_w{idx}_i{i}",prompt,1600 if scene else 64,None if scene else expected)
        with ThreadPoolExecutor(max_workers=level) as pool:rows=list(pool.map(one,range(level)))
        latencies=sorted(r['latency_seconds'] for r in rows);passed=sum(r['status']=='PASS' for r in rows)
        result=dict(concurrency=level,wave=idx,scene_prompt=scene,attempted=level,passed=passed,
                    wall_seconds=round(time.perf_counter()-start,3),median_seconds=statistics.median(latencies),
                    max_seconds=max(latencies),statuses=[r['status'] for r in rows])
        print(json.dumps(result),flush=True)
        return result

    summary=dict(model=MODEL,scope='DEVELOPMENT_ONLY',levels=[],last_passing_probe_level=0,smoke=[])
    for level in (1,2,4,6,8):
        good=True
        for idx in (1,2):
            result=wave(level,idx);summary['levels'].append(result);write(run/'summary.json',summary)
            if result['passed']!=level:good=False;break
        if not good:break
        summary['last_passing_probe_level']=level
    passing=summary['last_passing_probe_level']
    if passing:
        result=wave(min(4,passing),1,scene=True);summary['scene_load']=result
        if result['passed']==result['attempted']:
            summary['recommended_initial_concurrency']=min(4,passing)
            stop=False
            for item,g in zip(public,gold):
                candidate=None
                for role in ('direct','language','evidence'):
                    r=call(f"smoke_{item['case_id']}_{role}",request(item,role,candidate),1600)
                    if r['status']=='PASS':
                        policy,_=parse_response(r['raw_response'])
                        if role=='direct':candidate=policy
                        decision=execute(item['scene'],policy)
                        r.update(decision=decision,provisional_score=evaluate(policy,decision,g))
                        write(run/(r['call_id']+'.json'),r)
                    summary['smoke'].append({k:r[k] for k in ('call_id','status','latency_seconds','provisional_score') if k in r})
                    print(r['call_id'],r['status'],flush=True)
                    if r['status']!='PASS':stop=True;break
                if stop:break
    write(run/'summary.json',summary)
    print('DONE: '+str(run),flush=True)

if __name__=='__main__':main()
