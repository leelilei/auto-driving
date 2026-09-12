"""Fresh Haiku development run with an explicit, shared output contract."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import scene_pilot12 as s
from src.scene_policy import request as base_request,parse_response
from src.llm_client import LLM,load_config

CONTRACT='''
OUTPUT CONTRACT (applies to all fields):
Return one JSON object only, with no commentary before or after it and no Markdown fences.
It has exactly four keys: selection, availability_reference, return_by, evidence.
The first three fields follow the rules above. evidence MUST be a JSON object, never a string or array.
Inside evidence use field names as keys and instruction quotations as string values; an empty object {} is valid.
Do not add a verdict, explanation paragraph, corrected_policy wrapper, or any extra top-level key.
'''

def contracted_request(public,role,candidate=None):
    value=base_request(public,role,candidate);value['system']+=CONTRACT
    return value

def configure(run):
    m=s.verify(run)
    assert 'output_contract.txt' in m['files']
    assert (run/'output_contract.txt').read_text()==CONTRACT
    assert m['sources']['scripts/scene_haiku_contract.py']==s.digest(Path(__file__))
    s.request=contracted_request

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['run','replay','audit']);p.add_argument('--run-dir',type=Path)
    args=p.parse_args()
    if args.action in ('replay','audit'):
        if args.run_dir is None:raise ValueError('run directory required')
        configure(args.run_dir)
        if args.action=='replay':
            with s.NetworkBlocker():result=s.replay(args.run_dir,save=False)
            print(result['methods'])
        else:
            from scripts.audit_scene_haiku import main as audit
            sys.argv=['audit',str(args.run_dir)];audit()
        return
    run=ROOT/'results/scene_pilot12'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_xcode_haiku_scene12_contract')
    s.prepare(run,ROOT/'configs/scene_xcode_haiku.json',development_authorization='用户授权用Haiku跑最新设计；修复输出合同后的全新开发采集，人审仍PENDING。')
    (run/'output_contract.txt').write_text(CONTRACT)
    manifest=s.read(run/'manifest.json')
    manifest['files']['output_contract.txt']=s.digest(run/'output_contract.txt')
    manifest['sources']['scripts/scene_haiku_contract.py']=s.digest(Path(__file__))
    manifest.update(output_contract_revision='explicit-object-v1',preflight_calls=3,
                    reason='Previous run review outputs failed schema; no semantic rules, data, or scoring changed.')
    s.write(run/'manifest.json',manifest);configure(run)
    if not os.environ.get('XCODE_API_KEY'):
        r=subprocess.run(['security','find-generic-password','-s','XCODE_API_KEY','-w'],capture_output=True,text=True,check=True)
        os.environ['XCODE_API_KEY']=r.stdout.strip()
    print('RUN_DIR='+str(run),flush=True)
    case=s.read(run/'model_inputs.json')[0];candidate=None
    (run/'contract_preflight').mkdir()
    for role in s.ROLES:
        payload=contracted_request(case,role,candidate);llm=LLM(load_config(run/'config.json'))
        record=dict(request=payload,status='STARTED')
        path=run/'contract_preflight'/f'{role}.json';s.write(path,record)
        try:
            raw=llm.complete(**payload);record.update(raw_response=raw,provider_response=llm.client.last_response)
            policy,_=parse_response(raw)
            if role=='direct':candidate=policy
            record.update(status='PASS',policy=policy.to_dict())
        except Exception as e:
            record.update(status='FAILED',error_type=type(e).__name__)
        record['telemetry']=llm.telemetry;s.write(path,record)
        print('Contract preflight',role,record['status'],flush=True)
        if record['status']!='PASS':raise RuntimeError('Output contract preflight failed; full collection not started')
    s.collect(run,development=True)

if __name__=='__main__':main()
