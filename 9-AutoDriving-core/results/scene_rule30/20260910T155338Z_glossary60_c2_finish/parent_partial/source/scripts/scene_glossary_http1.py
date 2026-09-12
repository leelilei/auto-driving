"""Transport-only continuation; preserves completed glossary responses and failed parent ledger."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import scene_rule30_glossary as g
from src.llm_client import LLM,get_api_key

class CurlMessages:
    def __init__(self,config,key):self.config=config;self.key=key;self.last_response=None;self.last_usage=None
    def complete(self,prompt):
        c=self.config
        payload=dict(model=c.model,max_tokens=c.max_output_tokens or 1600,
             messages=[dict(role='user',content=prompt['user_prompt'].strip())],system=prompt['system_prompt'].strip())
        if not c.omit_temperature:payload['temperature']=c.temperature
        with tempfile.TemporaryDirectory(prefix='scene-http1-') as folder:
            body=Path(folder)/'request.json';reply=Path(folder)/'response.json'
            body.write_text(json.dumps(payload))
            headers='header = "x-api-key: '+self.key.replace('\\','\\\\').replace('"','\\"')+'"\n'
            headers+='header = "anthropic-version: 2023-06-01"\nheader = "content-type: application/json"\nheader = "User-Agent: Mozilla/5.0"\n'
            p=subprocess.run(['curl','--http1.1','--silent','--show-error','--max-time',str(c.timeout),
                  '--connect-timeout','15','--config','-','--data-binary','@'+str(body),
                  '--output',str(reply),'--write-out','%{http_code}',c.base_url.rstrip('/')+'/v1/messages'],
                  input=headers,text=True,capture_output=True,timeout=c.timeout+5)
            if p.returncode:raise RuntimeError('curl transport failure '+str(p.returncode)+': '+p.stderr.replace(self.key,'[REDACTED]'))
            status=int(p.stdout);text=reply.read_text()
            if status>=400:raise RuntimeError(f'provider HTTP {status}: '+text[:1000].replace(self.key,'[REDACTED]'))
            data=json.loads(text)
        self.last_response=data;self.last_usage=data.get('usage')
        raw=''.join(b.get('text','') for b in data.get('content',[]) if isinstance(b,dict))
        if not raw:raise RuntimeError('No text response')
        return raw

class CurlLLM(LLM):
    def __init__(self,config):
        super().__init__(config)
        self.client=CurlMessages(self.config,get_api_key(self.config.provider,self.config.api_key_env))

def prepare_continuation(parent,run):
    g.verify(parent)
    if (parent/'summary.json').exists():raise ValueError('parent already complete')
    g.prepare(run)
    inherited=[]
    for j in g.base.read(parent/'plan.json'):
        rs=g.attempts(parent,j['call_id'])
        if rs and rs[-1]['status'] in g.TERMINAL:
            if len(rs)!=1:raise ValueError('unexpected inherited retry sequence')
            name=j['call_id']+'.a1.json';shutil.copyfile(parent/'attempts'/name,run/'attempts'/name);inherited.append(name)
    shutil.copytree(parent,run/'parent_partial')
    config=g.base.read(run/'config.json');config['transport']='curl_http1';g.base.write(run/'config.json',config)
    g.base.write(run/'continuation.json',dict(parent=str(parent),parent_manifest_sha256=g.base.digest(parent/'manifest.json'),
          inherited_answers={f:g.base.digest(run/'attempts'/f) for f in inherited},
          reason='urllib TLS resets even at one request. Preserve valid answers, change only transport to curl HTTP/1.1.',
          parent_transport_failures=3,scope='Documented development transport revision; same prompts, candidates, model, temperature, output cap and scoring.'))
    m=g.base.read(run/'manifest.json')
    m.update(initial_concurrency=4,failure_concurrency=2,max_recoveries=3,
             transport='curl_http1',combined_request_budget=66,
             transport_revision='Parent failed calls retained separately; complete only remaining jobs. Max2 HTTP/1.1 attempts per pending job.')
    for f in [run/'config.json',run/'continuation.json',*list((run/'parent_partial').rglob('*'))]:
        if f.is_file():m['files'][str(f.relative_to(run))]=g.base.digest(f)
    name='scripts/scene_glossary_http1.py';shutil.copyfile(__file__,run/'source'/name)
    m['sources'][name]=g.base.digest(Path(__file__));g.base.write(run/'manifest.json',m);g.verify(run)

def audit(run):
    with g.base.NetworkBlocker():
        out=g.replay(run)
        if out!=g.base.read(run/'summary.json'):raise ValueError('summary mismatch')
        continuation=g.base.read(run/'continuation.json')
        for f,h in continuation['inherited_answers'].items():
            if g.base.digest(run/'attempts'/f)!=h:raise ValueError('inherited answer changed')
        rs=[g.base.read(f) for f in (run/'attempts').glob('*.json')]
        for r in rs:
            if r['status'] in g.TERMINAL:
                data=r['provider_response']
                assert data['model']==g.base.read(run/'config.json')['model']
                assert ''.join(b.get('text','') for b in data['content'] if isinstance(b,dict))==r['raw_response']
        total=out['physical_calls']+continuation['parent_transport_failures']
        if total>66:raise ValueError('combined call budget exceeded')
        g.base.write(run/'audit.json',dict(status='PASS_OFFLINE_MATCHED_CONTROL',independent_decisions=60,
             combined_physical_calls=total,inherited_answers=len(continuation['inherited_answers']),human_review='PENDING'))
        g.base.write(run/'delivery_integrity.json',{str(f.relative_to(run)):g.base.digest(f) for f in sorted(run.rglob('*')) if f.is_file() and f.name!='delivery_integrity.json'})
        print({k:v for k,v in out.items() if k!='rows'})

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['continue','audit']);p.add_argument('run',type=Path);a=p.parse_args()
    if a.action=='audit':audit(a.run);return
    run=ROOT/'results/scene_rule30'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_glossary60_http1')
    prepare_continuation(a.run,run);g.LLM=CurlLLM
    print('RUN_DIR='+str(run),flush=True);g.collect(run)

if __name__=='__main__':main()
