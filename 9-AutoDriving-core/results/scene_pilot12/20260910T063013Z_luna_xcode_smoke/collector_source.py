"""Explicitly authorized Luna development smoke; not human-reviewed evaluation."""
import json
import argparse
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.scene_pilot12 import read, write, digest, now
from src.scene_policy import request, parse_response, execute, evaluate
from src.llm_client import LLM, load_config

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--provider',choices=['fhl','xcode'],default='fhl')
    provider=parser.parse_args().provider
    key_name=provider.upper()+'_API_KEY'
    if not os.environ.get(key_name):
        key=subprocess.run(['security','find-generic-password','-s',key_name,'-w'],capture_output=True,text=True,check=True)
        os.environ[key_name]=key.stdout.strip()
    if not os.environ.get(key_name):raise RuntimeError(key_name+' missing')
    run=ROOT/'results/scene_pilot12'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+f'_luna_{provider}_smoke')
    run.mkdir(parents=True,exist_ok=False)
    config=read(ROOT/f'configs/v5/{provider}_gpt56_luna_120s.json')
    config.update(max_output_tokens=1600,retries=0,max_concurrency=1)
    write(run/'config.json',config)
    public=read(ROOT/'data/scene_pilot12_candidate/model_inputs.json')[:2]
    gold=read(ROOT/'data/scene_pilot12_candidate/gold_and_traces.json')[:2]
    write(run/'public.json',public);write(run/'gold.json',gold)
    shutil.copyfile(__file__,run/'collector_source.py')
    write(run/'manifest.json',dict(scope='UNREVIEWED_DEVELOPMENT_SMOKE',human_review='PENDING',
          authorization='User: 用luna模型试下',model=config['model'],provider=provider,
          planned_cases=['S01','S02'],planned_calls=6,repetitions=1,concurrency=1,retries=0,
          stopping='Stop on first transport or schema failure. No method ranking.',
          files={f:digest(run/f) for f in ('public.json','gold.json','config.json','collector_source.py')},
          policy_source_sha256=digest(ROOT/'src/scene_policy.py')))
    print('RUN_DIR='+str(run),flush=True)
    rows=[];stopped=False
    for item,g in zip(public,gold):
        direct=None
        for role in ('direct','language','evidence'):
            payload=request(item,role,direct)
            record=dict(case_id=item['case_id'],role=role,request=payload,status='STARTED',started=now())
            path=run/f"{item['case_id']}__{role}.json";write(path,record)
            llm=LLM(load_config(run/'config.json'))
            try:
                raw=llm.complete(**payload);record['raw_response']=raw
                policy,evidence=parse_response(raw)
                if role=='direct':direct=policy
                decision=execute(item['scene'],policy)
                record.update(status='COMPLETE',policy=policy.to_dict(),decision=decision,
                              provisional_score=evaluate(policy,decision,g))
            except Exception as exc:
                record.update(status='SCHEMA_FAILED' if 'raw_response' in record else 'TRANSPORT_FAILED',
                              error_type=type(exc).__name__,error_message=str(exc).replace(os.environ[key_name],'[REDACTED]'))
                stopped=True
            record.update(finished=now(),telemetry=llm.telemetry)
            write(path,record)
            rows.append(dict(case_id=item['case_id'],role=role,status=record['status'],
                             telemetry=llm.telemetry,provisional_score=record.get('provisional_score')))
            print(item['case_id'],role,record['status'],flush=True)
            if stopped:break
        if stopped:break
    write(run/'summary.json',dict(scope='UNREVIEWED_DEVELOPMENT_SMOKE',human_review='PENDING',
          model=config['model'],provider=provider,planned_calls=6,attempted_calls=len(rows),
          completed_calls=sum(r['status']=='COMPLETE' for r in rows),stopped_early=stopped,rows=rows))
    print('Smoke saved. No confirmatory claim.',flush=True)

if __name__=='__main__':main()
