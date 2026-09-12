"""Independent offline diagnostic; original outputs never modified."""
import sys,json,random,itertools,socket,hashlib
from pathlib import Path
from dataclasses import asdict
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[3]/'9-AutoDriving-core'
sys.path.insert(0,str(ROOT))
from src.graph import SyntheticGraph
from src.solver import ExactRouteSolver,RouteResult
from src.intent import Intent
from src.evaluation import check_route
import numpy as np

def blocked(*a,**k):raise RuntimeError('Offline network blocked')
socket.socket=blocked
run=ROOT/'results/runs/20260906T051339Z_main_test'
e1=ROOT/'results/v4_1/20260912T063836Z_e0_e1'
selections=[json.loads(s) for s in (e1/'e1/selections.jsonl').read_text().splitlines()]
items=[]
for f in sorted(run.glob('test_*.json')):
 if f.name.endswith('_graph.json'):continue
 g=json.loads(f.read_text());graph=SyntheticGraph.load(run/(g['group_id']+'_graph.json'));solver=ExactRouteSolver(graph)
 for u in g['utterances']:
  a=RouteResult(**u['routes']['A'])
  rev=solver.solve(**Intent.parse(u['candidates']['review']).solver_args()) if u['candidates'].get('review') else a
  gold=Intent.parse(u['gold_intent'])
  assert check_route(graph,a,gold)['task_success'] and check_route(graph,rev,gold)['task_success']
  items.append(dict(uid=u['utterance_id'],gid=u['group_id'],vt=u['variant_type'],a=asdict(a)['poi_ids'],r=asdict(rev)['poi_ids']))
assert len(items)==640
out={'scope':'GPT historical full160 only; all A/review routes gold task-success verified; not clean or confirmatory','route_types':{k:type(items[0][k]).__name__ for k in ('a','r')},'quotas':{}}
for q in (.05,.1,.2):
 rows=[r for r in selections if r['quota']==q];assert len(rows)==640
 rowmap={r['utterance_id']:r for r in rows}
 h={i for i,it in enumerate(items) if rowmap[it['uid']]['h']};non=[i for i in range(640) if i not in h];k=int(q*640)
 sets=[{i for i,it in enumerate(items) if rowmap[it['uid']]['darc_selected']},{i for i,it in enumerate(items) if rowmap[it['uid']]['b4_selected']}]
 for seed in range(20):
  perm=list(non);random.Random(seed).shuffle(perm);sets.append(h|set(perm[:k-len(h)]))
 assert all(len(s)==k and h<=s for s in sets)
 vals=[];bugs=[]
 for sel in sets:
  groups=defaultdict(list)
  for i,it in enumerate(items):groups[it['gid']].append(it['r'] if i in sel else it['a'])
  vals.append([sum(tuple(a)!=tuple(b) for a,b in itertools.combinations(rs,2))/6 for rs in groups.values()])
  bugs.append(np.mean([sum(a!=b for a,b in itertools.combinations(rs,2))/6 for rs in groups.values()]))
 v=np.array(vals);rng=np.random.default_rng(20260912);idx=rng.integers(0,160,size=(2000,160));d4=v[0]-v[1];d3=v[0]-v[2:].mean(axis=0)
 out['quotas'][str(q)]={'normalized_darc':float(v[0].mean()),'normalized_b4':float(v[1].mean()),'normalized_b3_mean':float(v[2:].mean()),'bug_reproduced_darc':float(bugs[0]),'bug_reproduced_b4':float(bugs[1]),'bug_reproduced_b3_mean':float(np.mean(bugs[2:])),'darc_minus_b3':float(d3.mean()),'ci95_darc_minus_b3':np.quantile(d3[idx].mean(axis=1),[.025,.975]).tolist(),'ci95_darc_minus_b4':np.quantile(d4[idx].mean(axis=1),[.025,.975]).tolist()}
p=Path(__file__).with_name('recheck_e1.json');p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
