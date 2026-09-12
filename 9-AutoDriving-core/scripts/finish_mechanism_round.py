"""One bounded transport recovery and offline logical ledger resolution."""
import json
import os
import shutil
import subprocess
from pathlib import Path
from dataclasses import replace
import mechanism_round as m

run=m.RUN.with_name(m.RUN.name+'_keychain')
m.RUN=run
m.verify()
jobs=json.loads((run/'requests.json').read_text())
failed=[j for j in jobs if json.loads((run/'attempts'/f"{j['id']}.json").read_text())['status']=='TRANSPORT_FAILED']
assert len(failed)<=1
key=subprocess.run(['security','find-generic-password','-s','DEEPSEEK_API_KEY','-w'],capture_output=True,text=True,check=True)
os.environ['DEEPSEEK_API_KEY']=key.stdout.strip()
for j in failed:
    cfg=replace(m.load_config(m.CONFIG),retries=0,max_concurrency=1,max_output_tokens=1600)
    rec=m.execute_call(m.LLM(cfg),run/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff',resume=True)
    print(j['id'],rec['status'],flush=True)

# Preserve physical attempts; create an explicit resolved view for original analyzer.
view=run/'resolved'
view.mkdir(exist_ok=True); (view/'attempts').mkdir(exist_ok=True)
for f in ['cases.json','requests.json','manifest.json']:
    shutil.copyfile(run/f,view/f)
resolution={}
for j in jobs:
    base=run/'attempts'/f"{j['id']}.json"
    second=base.with_name(base.stem+'.attempt2.json')
    selected=second if second.exists() else base
    target=view/'attempts'/base.name
    if not target.exists(): target.symlink_to(selected.resolve())
    resolution[j['id']]=str(selected.relative_to(run))
m.dump(run/'resolution.json',resolution)
m.RUN=view
m.analyze()
summary=json.loads((view/'summary.json').read_text())
physical=[json.loads(p.read_text()) for p in (run/'attempts').glob('*.json')]
summary['physical_attempts']=len(physical)
summary['physical_transport_failures']=sum(r['status']=='TRANSPORT_FAILED' for r in physical)
summary['unknown_failed_request_billing']=any((r.get('telemetry') or {}).get('usage_source')!='provider' for r in physical)
summary['cost_by_method']={role:{'provider_tokens':sum((r.get('telemetry') or {}).get('total_tokens',0) for r in physical
                                                if r['role']==role and (r.get('telemetry') or {}).get('usage_source')=='provider'),
                               'summed_attempt_latency_seconds':sum((r.get('telemetry') or {}).get('latency_seconds',0)
                                                                  for r in physical if r['role']==role)} for role in ('fields','darc')}
m.dump(run/'final_summary.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
