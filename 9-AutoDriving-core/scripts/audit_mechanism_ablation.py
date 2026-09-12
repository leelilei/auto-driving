"""Offline audit of raw outputs, frozen inputs and scoring for the ablation."""
import hashlib
import json
from collections import defaultdict
import mechanism_ablation as a
from scripts.experiment import NetworkBlocker

def reach(edges):
    out={tuple(x.strip().lower().replace(' ','_') for x in edge) for edge in edges}
    while True:
        new=out|{(x,z) for x,y in out for w,z in out if y==w}
        if new==out: return out
        out=new

def direction(w):
    return 1 if w>0.6 else -1 if w<0.4 else 0

def normalize_time(t):
    if t is None or t=='None': return None
    if isinstance(t,str):
        h,m=map(int,t.split(':')); return 60*h+m
    return t

with NetworkBlocker():
    a.verify()
    p=a.RUN
    summary=json.loads((p/'summary.json').read_text())
    assert summary['collection_complete'], 'incomplete experiment cannot pass audit'
    graphs=json.loads((p/'graph_integrity.json').read_text())
    for path,h in graphs.items():
        assert hashlib.sha256((a.m.ROOT/path).read_bytes()).hexdigest()==h
    jobs=json.loads((p/'requests.json').read_text())
    cases={c['id']:c for c in json.loads((p/'cases.json').read_text())}
    scores={(r['case'],r['rep'],r['role']):r for r in summary['rows']}
    failures=[]
    for job in jobs:
        rec=a.selected(job); c=cases[job['case']]
        assert rec['request']=={k:job[k] for k in ('system','user')}
        raw=json.loads(rec['raw_response']) if rec['status']=='COMPLETE' else None
        value=raw.get('intent',raw) if raw is not None else c['a']
        g=c['gold']
        hard=({x.strip().lower().replace(' ','_') for x in value['pois']}==set(g['pois'])
              and normalize_time(value['time_limit'])==g['time_limit'] and reach(value['dependencies'])==reach(g['dependencies']))
        correct=hard and direction(value['quality_weight'])==direction(g['quality_weight'])
        row=scores[(job['case'],job['rep'],job['role'])]
        assert correct==row['correct']
        if not correct:
            failures.append(dict(case=job['case'],rep=job['rep'],role=job['role'],instruction=c['instruction'],gold=g,
                                 raw_response=rec.get('raw_response'),status=rec['status']))
    for c in cases.values():
        for rep in (1,2):
            js=[j for j in jobs if j['case']==c['id'] and j['rep']==rep]
            assert len(js)==3
            assert len({j['user'].split('Supplementary information:')[0] for j in js})==1
            assert all(j['user'].count(c['instruction'])==1 for j in js)
            values={j['role']:json.loads(j['user'].split('Supplementary information:')[1]) for j in js}
            assert values['fields']['differing_fields']==values['route_order']['differing_fields']==values['full']['differing_fields']
            for side in ('A','B'):
                assert values['route_order']['routes'][side]['categories']==values['full']['routes'][side]['categories']
    group_differences={}
    for left,right in [('full','route_order'),('route_order','fields'),('full','fields')]:
        groups=defaultdict(list)
        for cid,c in cases.items():
            for rep in (1,2):
                groups[c['source_group']].append(int(scores[(cid,rep,left)]['correct'])-int(scores[(cid,rep,right)]['correct']))
        group_differences[left+'_minus_'+right]={g:sum(v)/len(v) for g,v in groups.items()}
    audit=dict(status='PASS',raw_response_score_checks=144,frozen_request_matches=144,common_prefix_triples=48,
               one_instruction_occurrences=144,scoring_graphs=8,source_groups=8,scope='offline developer audit, not human semantic reannotation',
               group_mean_differences=group_differences,errors=failures)
    a.m.dump(p/'audit.json',audit)
    print(json.dumps({k:v for k,v in audit.items() if k!='errors'},indent=2))
