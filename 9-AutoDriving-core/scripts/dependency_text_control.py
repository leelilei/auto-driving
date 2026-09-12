"""Fresh paired DS calls: verbalized candidate dependencies versus planned route order."""
import argparse
import json
import os
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import mechanism_ablation as old
from scripts.collect_v5_diagnostic import parse_response
from scripts.experiment import NetworkBlocker

m=old.m
RUN=m.ROOT/'results/v5/diagnostic/20260910_ds_dependency_text_control24'
ROLES=('dependency_text','route_order')

def dependency_text(candidate):
    """Pure rendering: no instruction, gold, graph or solver input."""
    edges=candidate['dependencies']
    return [f"Visit {a.replace('_',' ')} before {b.replace('_',' ')}." for a,b in edges] or ['No visit-order requirement is specified in this candidate.']

def prepare():
    assert not RUN.exists()
    cases=json.loads((old.RUN/'cases.json').read_text())
    graph_hashes=json.loads((old.RUN/'graph_integrity.json').read_text())
    assert dependency_text({'dependencies':[]})==['No visit-order requirement is specified in this candidate.']
    assert dependency_text({'dependencies':[['bank','library']]})==['Visit bank before library.']
    jobs=[]
    for rep in (1,2):
        for i,c in enumerate(cases):
            prefix=old.HEADER+'\nInstruction:\n'+c['instruction']+'\n\nCandidate A:\n'+json.dumps(c['a'],sort_keys=True)+'\n\nCandidate B:\n'+json.dumps(c['b'],sort_keys=True)+'\n\nSupplementary information:\n'
            fields={'differing_fields':c['report']['differing_fields']}
            dep={**fields,'candidate_order_requirements':{'A':dependency_text(c['a']),'B':dependency_text(c['b'])}}
            route={**fields,'routes':{side:{'categories':r['categories']} for side,r in c['report']['routes'].items()}}
            vals={'dependency_text':dep,'route_order':route}
            for role in (ROLES if (i+rep)%2==0 else ROLES[::-1]):
                user=prefix+json.dumps(vals[role],sort_keys=True)
                assert user.count(c['instruction'])==1
                jobs.append(dict(id=f"{c['id']}__r{rep}__{role}",case=c['id'],rep=rep,role=role,
                                 system='Return only the requested JSON object.',user=user))
    assert len(jobs)==96 and len({j['id'] for j in jobs})==96
    for c in cases:
        for rep in (1,2):
            pair=[j for j in jobs if j['case']==c['id'] and j['rep']==rep]
            assert len({j['user'].split('Supplementary information:')[0] for j in pair})==1
    RUN.mkdir(parents=True);(RUN/'attempts').mkdir()
    m.dump(RUN/'cases.json',cases);m.dump(RUN/'requests.json',jobs);m.dump(RUN/'graph_integrity.json',graph_hashes)
    config=json.loads(m.CONFIG.read_text());config.update(timeout=120,max_output_tokens=1600,max_concurrency=1,retries=0)
    m.dump(RUN/'config.json',config)
    inputs={str(p.relative_to(m.ROOT)):m.digest(p) for p in [Path(__file__),Path(old.__file__),Path(m.__file__),m.ROOT/'scripts/collect_v5_diagnostic.py',m.ROOT/'src/llm_client.py']}
    m.dump(RUN/'manifest.json',dict(created=m.stamp(),scope='controlled_development_no_new_human_annotation',
            planned=96,cases=24,mother_groups=8,repetitions=2,concurrency=8,timeout=120,max_output_tokens=1600,
            source_cases_sha256=m.digest(old.RUN/'cases.json'),inputs=inputs,
            frozen={f:m.digest(RUN/f) for f in ['cases.json','requests.json','config.json','graph_integrity.json']},
            primary='route_order minus dependency_text semantic correctness; hard AND preference direction',
            secondary='TSR, raw correctness, correction/damage against A, token cost, per-repeat and mother-group results',
            recovery='max one transport recovery per logical request, at most16 recoveries; no retry of schema or valid responses; authentication error or all failed batch stops',
            interpretation='8 mother groups only; descriptive development evidence; both arms freshly sampled, old answers not reused; dependency text needs no planner but differs from route in wording and total/partial-order information'))
    print('FROZEN: 24 cases, 96 fresh requests; pure dependency renderer and 48 shared prefixes checked',flush=True)

def verify():
    manifest=json.loads((RUN/'manifest.json').read_text())
    for p,h in manifest['inputs'].items():assert m.digest(m.ROOT/p)==h,p
    for f,h in manifest['frozen'].items():assert m.digest(RUN/f)==h,f
    for p,h in json.loads((RUN/'graph_integrity.json').read_text()).items():assert m.digest(m.ROOT/p)==h,p

def selected(j):
    files=list((RUN/'attempts').glob(j['id']+'*.json'))
    records=[json.loads(p.read_text()) for p in files]
    terminal=[r for r in records if r['status'] in ('COMPLETE','SCHEMA_FAILED')]
    assert len(terminal)<=1
    return terminal[0] if terminal else (records[-1] if records else None)

def collect():
    verify()
    key=subprocess.run(['security','find-generic-password','-s','DEEPSEEK_API_KEY','-w'],capture_output=True,text=True,check=True)
    os.environ['DEEPSEEK_API_KEY']=key.stdout.strip()
    cfg=m.load_config(RUN/'config.json')
    jobs=json.loads((RUN/'requests.json').read_text())
    def call(j):
        prior=selected(j)
        if prior:return prior
        return m.execute_call(m.LLM(cfg),RUN/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff')
    def fatal(rs):return any('401' in r.get('error_message','') or '403' in r.get('error_message','') for r in rs)
    first=call(jobs[0]);print('Real preflight',first['status'],flush=True)
    if first['status']=='TRANSPORT_FAILED':analyze();return
    with ThreadPoolExecutor(max_workers=8) as pool:
        for start in range(1,len(jobs),8):
            rs=list(pool.map(call,jobs[start:start+8]))
            print('Progress',min(start+8,len(jobs)),dict(Counter(r['status'] for r in rs)),flush=True)
            if fatal(rs) or all(r['status']=='TRANSPORT_FAILED' for r in rs):break
    failures=[j for j in jobs if selected(j) and selected(j)['status']=='TRANSPORT_FAILED']
    if len(failures)<=16 and not fatal([selected(j) for j in failures]):
        for j in failures:
            if (RUN/'attempts'/f"{j['id']}.attempt2.json").exists():continue
            r=m.execute_call(m.LLM(cfg),RUN/'attempts'/f"{j['id']}.json",j['id'],j['role'],j['system'],j['user'],'tradeoff',resume=True)
            print('Recovery',j['id'],r['status'],flush=True)
            if r['status']=='TRANSPORT_FAILED':break
    analyze()

def analyze():
    verify()
    jobs=json.loads((RUN/'requests.json').read_text());cases={c['id']:c for c in json.loads((RUN/'cases.json').read_text())}
    physical=[json.loads(p.read_text()) for p in (RUN/'attempts').glob('*.json')]
    records={j['id']:selected(j) for j in jobs}
    complete=all(r and r['status'] in ('COMPLETE','SCHEMA_FAILED') for r in records.values())
    summary=dict(collection_complete=complete,planned=96,physical_attempts=len(physical),
                 statuses=dict(Counter(r['status'] if r else 'MISSING' for r in records.values())),
                 transport_failures=sum(r['status']=='TRANSPORT_FAILED' for r in physical),
                 unknown_failed_request_billing=any((r.get('telemetry') or {}).get('usage_source')!='provider' for r in physical))
    if complete:
        rows=[]
        for j in jobs:
            c=cases[j['case']];r=records[j['id']]
            assert r['request']=={k:j[k] for k in ('system','user')}
            raw=parse_response(r['raw_response'])[0] if r['status']=='COMPLETE' else None
            if raw:assert m.intent_dict(raw)==r['parsed_intent']
            graph=m.SyntheticGraph.load(m.ROOT/c['graph']);gold=m.Intent.parse(c['gold'])
            effective=raw or m.Intent.parse(c['a']);sc=m.scores(effective,gold,graph)
            rows.append(dict(case=j['case'],rep=j['rep'],role=j['role'],group=c['source_group'],family=c['family'],**sc,
                             raw_correct=m.scores(raw,gold,graph)['correct'],fallback=raw is None,
                             corrected=not c['baseline']['correct'] and sc['correct'],damaged=c['baseline']['correct'] and not sc['correct']))
        summary['rows']=rows
        summary['methods']={role:{'n':48,**{k:sum(r[k] for r in rows if r['role']==role) for k in ('correct','hard','direction','tsr','raw_correct','corrected','damaged','fallback')},
            'tokens':sum((r.get('telemetry') or {}).get('total_tokens',0) for r in physical if r['role']==role and (r.get('telemetry') or {}).get('usage_source')=='provider')} for role in ROLES}
        lookup={(r['case'],r['rep'],r['role']):r for r in rows};wins=[];losses=[]
        for cid in cases:
            for rep in (1,2):
                dep=lookup[cid,rep,'dependency_text']['correct'];route=lookup[cid,rep,'route_order']['correct']
                if route and not dep:wins.append([cid,rep])
                if dep and not route:losses.append([cid,rep])
        summary['route_vs_dependency']={'wins':wins,'losses':losses}
        summary['by_rep']={rep:{role:sum(r['correct'] for r in rows if r['rep']==rep and r['role']==role) for role in ROLES} for rep in (1,2)}
        summary['by_family']={fam:{role:sum(r['correct'] for r in rows if r['family']==fam and r['role']==role) for role in ROLES} for fam in sorted({c['family'] for c in cases.values()})}
    m.dump(RUN/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2),flush=True)

def audit():
    with NetworkBlocker():
        analyze()
        summary=json.loads((RUN/'summary.json').read_text());assert summary['collection_complete']
        jobs=json.loads((RUN/'requests.json').read_text());cases={c['id']:c for c in json.loads((RUN/'cases.json').read_text())}
        lookup={(r['case'],r['rep'],r['role']):r for r in summary['rows']}
        for j in jobs:
            c=cases[j['case']];r=selected(j)
            x=json.loads(r['raw_response']) if r['status']=='COMPLETE' else {'intent':c['a']}
            x=x.get('intent',x);g=c['gold']
            norm=lambda v:v.strip().lower().replace(' ','_')
            t=x['time_limit']
            if isinstance(t,str):
                t=None if t=='None' else sum(int(v)*scale for v,scale in zip(t.split(':'),(60,1)))
            edges={tuple(map(norm,p)) for p in x['dependencies']}
            while True:
                expanded=edges|{(u,z) for u,v in edges for w,z in edges if v==w}
                if expanded==edges:break
                edges=expanded
            hard=set(map(norm,x['pois']))==set(g['pois']) and t==g['time_limit'] and edges=={tuple(p) for p in g['dependencies']}
            direction=lambda w:1 if w>.6 else -1 if w<.4 else 0
            correct=hard and direction(x['quality_weight'])==direction(g['quality_weight'])
            assert correct==lookup[j['case'],j['rep'],j['role']]['correct']
            payload=json.loads(j['user'].split('Supplementary information:')[1])
            if j['role']=='dependency_text':assert payload['candidate_order_requirements']=={'A':dependency_text(c['a']),'B':dependency_text(c['b'])}
            else:
                for side in ('A','B'):assert payload['routes'][side]['categories']==c['report']['routes'][side]['categories']
        m.dump(RUN/'audit.json',dict(status='PASS',independent_raw_scores=96,frozen_requests=96,payload_checks=96,graphs=8,mother_groups=8,network='socket blocked; no API calls',scope='developer audit, not new human annotation'))
        print('AUDIT PASS',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','collect','analyze','audit'])
    globals()[p.parse_args().action]()
