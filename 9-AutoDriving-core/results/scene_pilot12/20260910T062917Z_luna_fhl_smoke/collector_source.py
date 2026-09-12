"""Explicitly authorized Luna development smoke; not human-reviewed evaluation."""
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.scene_pilot12 import read, write, digest, now
from src.scene_policy import request, parse_response, execute, evaluate
from src.llm_client import LLM, load_config

def main():
    if not os.environ.get('FHL_API_KEY'):raise RuntimeError('FHL_API_KEY missing')
    run=ROOT/'results/scene_pilot12'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_luna_fhl_smoke')
    run.mkdir(parents=True,exist_ok=False)
    config=read(ROOT/'configs/v5/fhl_gpt56_luna_120s.json')
    config.update(max_output_tokens=1600,retries=0,max_concurrency=1)
    write(run/'config.json',config)
    public=read(ROOT/'data/scene_pilot12_candidate/model_inputs.json')[:2]
    gold=read(ROOT/'data/scene_pilot12_candidate/gold_and_traces.json')[:2]
    write(run/'public.json',public);write(run/'gold.json',gold)
    shutil.copyfile(__file__,run/'collector_source.py')
    write(run/'manifest.json',dict(scope='UNREVIEWED_DEVELOPMENT_SMOKE',human_review='PENDING',
          authorization='User: 用luna模型试下',model=config['model'],provider='fhl',
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
                              error_type=type(exc).__name__,error_message=str(exc).replace(os.environ['FHL_API_KEY'],'[REDACTED]'))
                stopped=True
            record.update(finished=now(),telemetry=llm.telemetry)
            write(path,record)
            rows.append(dict(case_id=item['case_id'],role=role,status=record['status'],
                             telemetry=llm.telemetry,provisional_score=record.get('provisional_score')))
            print(item['case_id'],role,record['status'],flush=True)
            if stopped:break
        if stopped:break
    write(run/'summary.json',dict(scope='UNREVIEWED_DEVELOPMENT_SMOKE',human_review='PENDING',
          model=config['model'],provider='fhl',planned_calls=6,attempted_calls=len(rows),
          completed_calls=sum(r['status']=='COMPLETE' for r in rows),stopped_early=stopped,rows=rows))
    print('Smoke saved. No confirmatory claim.',flush=True)

if __name__=='__main__':main()
