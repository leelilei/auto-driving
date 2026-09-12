"""Luna/FHL replication of the frozen 144-request information ablation."""
import argparse
import json
import os
import runpy
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import mechanism_ablation as a

REFERENCE=a.RUN
a.RUN=a.m.ROOT/'results/v5/diagnostic/20260910_fhl_luna_mechanism_ablation24'
a.m.CONFIG=a.m.ROOT/'configs/v5/fhl_gpt56_luna_120s.json'

def prepare():
    a.prepare()
    assert (a.RUN/'requests.json').read_bytes()==(REFERENCE/'requests.json').read_bytes()
    assert (a.RUN/'cases.json').read_bytes()==(REFERENCE/'cases.json').read_bytes()
    shutil.copyfile(REFERENCE/'graph_integrity.json',a.RUN/'graph_integrity.json')
    manifest=json.loads((a.RUN/'manifest.json').read_text())
    manifest.update(replication_of=str(REFERENCE.relative_to(a.m.ROOT)),wrapper_sha256=a.m.digest(Path(__file__)),
                    decoding_note='FHL Luna config omits temperature, unlike DeepSeek temperature=0; compare within-model information effects, not intrinsic model ability.',
                    stopping='Preflight first three planned real requests serially, then concurrency4; one recovery per transport unit, maximum16 recoveries. Stop on authentication failure or four consecutive failed requests in a batch. Never retry schema failure or valid answers.',
                    timeout=120,concurrency=4)
    a.m.dump(a.RUN/'manifest.json',manifest)

def verify():
    a.verify()
    manifest=json.loads((a.RUN/'manifest.json').read_text())
    assert a.m.digest(Path(__file__))==manifest['wrapper_sha256']

def collect():
    verify()
    assert os.environ.get('FHL_API_KEY'), 'FHL_API_KEY is missing'
    cfg=replace(a.m.load_config(a.m.CONFIG),retries=0,max_concurrency=1,max_output_tokens=1600)
    jobs=json.loads((a.RUN/'requests.json').read_text())
    def call(j):
        previous=a.selected(j)
        if previous: return previous
        return a.m.execute_call(a.m.LLM(cfg),a.RUN/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff')
    def fatal(rs):
        return any('401' in r.get('error_message','') or '403' in r.get('error_message','') for r in rs)
    def recover(j):
        r=a.selected(j)
        if r['status']!='TRANSPORT_FAILED' or fatal([r]):return r
        second=a.RUN/'attempts'/f"{j['id']}.attempt2.json"
        if second.exists():return r
        used=len(list((a.RUN/'attempts').glob('*.attempt2.json')))
        if used>=16:return r
        return a.m.execute_call(a.m.LLM(cfg),a.RUN/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff',resume=True)
    for j in jobs[:3]:
        r=call(j)
        if r['status']=='TRANSPORT_FAILED':r=recover(j)
        print('Real prompt preflight',j['id'],r['status'],flush=True)
        if r['status']=='TRANSPORT_FAILED':a.analyze();return
    with ThreadPoolExecutor(max_workers=4) as pool:
        for start in range(3,len(jobs),4):
            rs=list(pool.map(call,jobs[start:start+4]))
            print('Progress',min(start+4,len(jobs)),dict(a.Counter(r['status'] for r in rs)),flush=True)
            if fatal(rs) or all(r['status']=='TRANSPORT_FAILED' for r in rs):break
    failed=[j for j in jobs if a.selected(j) and a.selected(j)['status']=='TRANSPORT_FAILED']
    if len(failed)<=16 and not fatal([a.selected(j) for j in failed]):
        for j in failed:
            r=recover(j);print('Recovery',j['id'],r['status'],flush=True)
            if r['status']=='TRANSPORT_FAILED':break
    a.analyze()

def audit():
    verify()
    runpy.run_path(str(a.m.ROOT/'scripts/audit_mechanism_ablation.py'),run_name='__main__')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','collect','analyze','audit'])
    args=p.parse_args()
    if args.action=='analyze':verify();a.analyze()
    else:globals()[args.action]()
