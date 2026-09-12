"""Fixed-case, common-prompt, three-level information ablation (two repetitions)."""
import argparse
import copy
import json
import os
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import mechanism_round as m

RUN=m.ROOT/'results/v5/diagnostic/20260910_mechanism_ablation24'
SOURCE=m.ROOT/'results/v5/diagnostic/20260910_controlled_mechanism24_keychain'
ROLES=('fields','route_order','full')
HEADER='''Resolve two candidate interpretations of one route-planning instruction. The instruction is the sole authority. Both candidates may be wrong, including when they agree. Supplementary information describes candidate differences or planning consequences; it does not identify the correct intent. Resolve every field from the instruction. Do not infer user preference from a route or map.
Return one JSON object only:
{"intent":{"pois":[],"time_limit":null,"dependencies":[],"quality_weight":0.5},"evidence":{},"changes":[]}
Evidence must quote short spans from the instruction. Changes must name every candidate field you revised.
'''

def prepare():
    assert not RUN.exists(), 'frozen directory already exists'
    old=json.loads((SOURCE/'manifest.json').read_text())
    assert m.digest(SOURCE/'cases.json')==old['cases_sha256']
    cases=json.loads((SOURCE/'cases.json').read_text())
    jobs=[]
    for rep in range(2):
        for i,c in enumerate(cases):
            report=copy.deepcopy(c['report'])
            fields={'differing_fields':report['differing_fields']}
            routes={**fields,'routes':{k:{'categories':v['categories']} for k,v in report['routes'].items()}}
            full={k:v for k,v in report.items() if k not in ('instruction','candidate_A','candidate_B','candidate_evidence','report_version')}
            prefix=HEADER+'\nInstruction:\n'+c['instruction']+'\n\nCandidate A:\n'+json.dumps(c['a'],sort_keys=True)+'\n\nCandidate B:\n'+json.dumps(c['b'],sort_keys=True)+'\n\nSupplementary information:\n'
            values={'fields':fields,'route_order':routes,'full':full}
            # Rotate scheduling order independently of outcomes.
            order=ROLES[(i+rep)%3:]+ROLES[:(i+rep)%3]
            for role in order:
                user=prefix+json.dumps(values[role],sort_keys=True)
                assert user.count(c['instruction'])==1
                assert 'gold' not in json.dumps(values[role]).lower()
                jobs.append(dict(id=f"{c['id']}__r{rep+1}__{role}",case=c['id'],rep=rep+1,role=role,
                                 system='Return only the requested JSON object.',user=user))
    assert len(jobs)==144 and len({j['id'] for j in jobs})==144
    RUN.mkdir(parents=True); (RUN/'attempts').mkdir()
    m.dump(RUN/'cases.json',cases); m.dump(RUN/'requests.json',jobs)
    m.dump(RUN/'manifest.json',dict(created=m.stamp(),scope='controlled_development_ablation_not_confirmatory',
           source_cases_sha256=m.digest(SOURCE/'cases.json'),cases_sha256=m.digest(RUN/'cases.json'),
           requests_sha256=m.digest(RUN/'requests.json'),script_sha256=m.digest(Path(__file__)),
           config_sha256=m.digest(m.CONFIG),model=json.loads(m.CONFIG.read_text())['model'],
           cases=24,source_groups=8,repetitions=2,planned=144,concurrency=4,max_output_tokens=1600,
           primary='full minus route_order semantic correctness, paired within case and repetition',
           secondary='route_order minus fields; TSR; correction/damage against fixed A; tokens',
           stopping='first authentication error halts; at most one transport recovery per unit, at most 8 recoveries total; no schema retries',
           interpretation='No independent sample inflation; descriptive repeats only; no causal claim about numerical values alone because full adds swaps and constraints too; more tokens not equal budget',
           original_experiment='New common instruction explicitly mentions common errors in every arm; do not compare absolute scores causally with previous round'))
    print('Frozen 144 requests; common prefix, one instruction occurrence, no gold in supplementary payload',flush=True)

def verify():
    manifest=json.loads((RUN/'manifest.json').read_text())
    for file,key in [('cases.json','cases_sha256'),('requests.json','requests_sha256')]:
        assert m.digest(RUN/file)==manifest[key]
    assert m.digest(Path(__file__))==manifest['script_sha256']
    assert m.digest(m.CONFIG)==manifest['config_sha256']

def selected(job):
    files=sorted((RUN/'attempts').glob(job['id']+'*.json'))
    records=[json.loads(f.read_text()) for f in files]
    valid=[r for r in records if r['status'] in ('COMPLETE','SCHEMA_FAILED')]
    assert len(valid)<=1
    return valid[0] if valid else (records[-1] if records else None)

def collect():
    verify()
    key=subprocess.run(['security','find-generic-password','-s','DEEPSEEK_API_KEY','-w'],capture_output=True,text=True,check=True)
    os.environ['DEEPSEEK_API_KEY']=key.stdout.strip()
    cfg=replace(m.load_config(m.CONFIG),retries=0,max_concurrency=1,max_output_tokens=1600)
    jobs=json.loads((RUN/'requests.json').read_text())
    def call(job):
        previous=selected(job)
        if previous: return previous
        return m.execute_call(m.LLM(cfg),RUN/'attempts'/f"{job['id']}.json",job['id'],job['role'],job['system'],job['user'],'tradeoff')
    def fatal(records):
        return any('401' in r.get('error_message','') or '403' in r.get('error_message','') for r in records)
    first=call(jobs[0]); print('Precheck',first['status'],flush=True)
    if first['status']=='TRANSPORT_FAILED':
        analyze(); return
    with ThreadPoolExecutor(max_workers=4) as pool:
        for start in range(1,len(jobs),4):
            records=list(pool.map(call,jobs[start:start+4]))
            print('Progress',min(start+4,len(jobs)),dict(Counter(r['status'] for r in records)),flush=True)
            if fatal(records): break
    failures=[j for j in jobs if selected(j) and selected(j)['status']=='TRANSPORT_FAILED']
    if len(failures)<=8 and not fatal([selected(j) for j in failures]):
        for j in failures:
            second=RUN/'attempts'/f"{j['id']}.attempt2.json"
            if second.exists(): continue
            r=m.execute_call(m.LLM(cfg),RUN/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff',resume=True)
            print('Bounded recovery',j['id'],r['status'],flush=True)
            if fatal([r]): break
    analyze()

def analyze():
    verify()
    jobs=json.loads((RUN/'requests.json').read_text())
    cases={c['id']:c for c in json.loads((RUN/'cases.json').read_text())}
    records={j['id']:selected(j) for j in jobs}
    physical=[json.loads(p.read_text()) for p in (RUN/'attempts').glob('*.json')]
    complete=all(r and r['status'] in ('COMPLETE','SCHEMA_FAILED') for r in records.values())
    result=dict(collection_complete=complete,planned=144,physical_attempts=len(physical),
                statuses=dict(Counter(r['status'] if r else 'MISSING' for r in records.values())),
                physical_transport_failures=sum(r['status']=='TRANSPORT_FAILED' for r in physical),
                unknown_failed_request_billing=any((r.get('telemetry') or {}).get('usage_source')!='provider' for r in physical))
    rows=[]
    if complete:
        for j in jobs:
            c=cases[j['case']]; r=records[j['id']]
            assert r['request']=={k:j[k] for k in ['system','user']}
            raw=None
            if r['status']=='COMPLETE':
                from scripts.collect_v5_diagnostic import parse_response
                raw=parse_response(r['raw_response'])[0]
                assert m.intent_dict(raw)==r['parsed_intent']
            graph=m.SyntheticGraph.load(m.ROOT/c['graph']); gold=m.Intent.parse(c['gold'])
            effective=raw or m.Intent.parse(c['a']); sc=m.scores(effective,gold,graph)
            rows.append(dict(case=j['case'],family=c['family'],group=c['source_group'],rep=j['rep'],role=j['role'],
                             raw_correct=m.scores(raw,gold,graph)['correct'],fallback=raw is None,**sc,
                             corrected=not c['baseline']['correct'] and sc['correct'],damaged=c['baseline']['correct'] and not sc['correct']))
        result['methods']={role:{'n':48,**{key:sum(r[key] for r in rows if r['role']==role) for key in ('correct','tsr','corrected','damaged','fallback')},
                          'tokens':sum((r.get('telemetry') or {}).get('total_tokens',0) for r in physical if r['role']==role and (r.get('telemetry') or {}).get('usage_source')=='provider')}
                          for role in ROLES}
        result['by_rep']={str(rep):{role:sum(r['correct'] for r in rows if r['role']==role and r['rep']==rep) for role in ROLES} for rep in (1,2)}
        result['by_family']={fam:{role:sum(r['correct'] for r in rows if r['role']==role and r['family']==fam) for role in ROLES} for fam in sorted({c['family'] for c in cases.values()})}
        result['paired']={}
        for a,b in [('full','route_order'),('route_order','fields'),('full','fields')]:
            pairs=[({r['role']:r['correct'] for r in rows if r['case']==cid and r['rep']==rep}) for cid in cases for rep in (1,2)]
            result['paired'][a+'_minus_'+b]={'wins':sum(p[a] and not p[b] for p in pairs),'losses':sum(p[b] and not p[a] for p in pairs)}
        result['rows']=rows
    m.dump(RUN/'summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','collect','analyze'])
    globals()[p.parse_args().action]()
