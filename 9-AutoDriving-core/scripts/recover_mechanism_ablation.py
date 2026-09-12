"""Explicit transport-only amendment; never overwrite existing model answers."""
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import mechanism_ablation as a

a.verify()
assert (a.RUN/'transport_amendment.json').exists()
jobs=json.loads((a.RUN/'requests.json').read_text())
assert all(a.selected(j) is not None for j in jobs), 'wait for first pass to finish'
failures=[j for j in jobs if a.selected(j)['status']=='TRANSPORT_FAILED']
assert len(failures)<=16, 'amended recovery limit exceeded'
assert not any('401' in a.selected(j).get('error_message','') or '403' in a.selected(j).get('error_message','') for j in failures)
key=subprocess.run(['security','find-generic-password','-s','DEEPSEEK_API_KEY','-w'],capture_output=True,text=True,check=True)
os.environ['DEEPSEEK_API_KEY']=key.stdout.strip()
cfg=replace(a.m.load_config(a.m.CONFIG),retries=0,max_concurrency=1,max_output_tokens=1600,timeout=120)
def recover(j):
    second=a.RUN/'attempts'/f"{j['id']}.attempt2.json"
    if second.exists(): return json.loads(second.read_text())
    return a.m.execute_call(a.m.LLM(cfg),a.RUN/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff',resume=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0,len(failures),4):
        results=list(pool.map(recover,failures[start:start+4]))
        for r in results:print(r['call_id'],r['status'],flush=True)
        if any('401' in r.get('error_message','') or '403' in r.get('error_message','') for r in results):break
a.analyze()
