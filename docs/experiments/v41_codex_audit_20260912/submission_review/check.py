import json,sys,socket,itertools,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[4]/'9-AutoDriving-core'
sys.path.insert(0,str(ROOT))
from src.graph import SyntheticGraph
from src.solver import RouteResult, ExactRouteSolver
from src.intent import Intent
from src.evaluation import check_route

def blocked(*a,**k):raise RuntimeError('offline')
socket.socket=blocked
old=json.loads((ROOT/'data/e2/e2_confirmation_utterances.json').read_text());new=json.loads((ROOT/'data/e2/e2_strictly_unexposed_utterances.json').read_text())
result={'overlap_old_e2':sorted({x['source_cluster_id'] for x in old}&{x['source_cluster_id'] for x in new}),'runs':{}}
for name in ['20260912T073141Z_e2_confirmation_gemini-3_1-flash-lite','20260912T074558Z_e2_confirmation_gpt-5_6-luna']:
 d=ROOT/'results/runs'/name
 us=[];graphs={}
 for f in sorted(d.glob('e2_clean_*.json')):
  if f.name.endswith('_graph.json'):continue
  g=json.loads(f.read_text());graphs[g['group_id']]=SyntheticGraph.load(d/(g['group_id']+'_graph.json'));us+=g['utterances']
 for u in us:
  if u['routes'].get('review') is None and u['candidates'].get('review'):
   from dataclasses import asdict
   u['routes']['review']=asdict(ExactRouteSolver(graphs[u['group_id']]).solve(**Intent.parse(u['candidates']['review']).solver_args()))
  if not u['candidates'].get('review'):u['routes']['review']=u['routes'].get('A')
 assert len(us)==160 and len({u['utterance_id'] for u in us})==160
 checks={'candidate_exact_match':0,'usage_missing':0,'returned_model_saved':0,'review_invalid_fallback':sum(not u['candidates'].get('review') for u in us)}
 for u in us:
  q=json.loads(u['calls']['review']['user_prompt'])
  checks['candidate_exact_match']+=q['candidate_A']==u['candidates']['A'] and q['candidate_B']==u['candidates']['B'] and q['instruction']==u['text']
  for c in u['calls'].values():
   checks['usage_missing']+=c.get('usage') is None
   checks['returned_model_saved']+='model' in c or 'returned_model' in c
 rows=[json.loads(l) for l in (d/'equal_quota_selections.jsonl').read_text().splitlines()];sel={r['utterance_id']:r for r in rows if r['quota']==.1}
 methods=['B0','B6','darc_selected','b4_selected']+[f'b3_selected_seed{s}' for s in range(20)]
 maps={};fail={}
 for m in methods:
  maps[m]={};fail[m]=[]
  for u in us:
   choice='A' if m=='B0' else 'review' if m=='B6' or sel[u['utterance_id']][m] else 'A'
   route=RouteResult(**u['routes'][choice]) if u['routes'].get(choice) else None;ok=check_route(graphs[u['group_id']],route,Intent.parse(u['gold_intent']))['task_success']
   maps[m][(u['group_id'],u['variant_type'])]=(tuple(route.poi_ids) if route else (),ok)
   if not ok:fail[m].append(u['utterance_id'])
 pairs=[(gid,a,b) for gid in graphs for a,b in itertools.combinations(['V0','V1','V2','V3'],2)]
 cmp=methods[2:];common=[p for p in pairs if all(maps[m][(p[0],p[1])][1] and maps[m][(p[0],p[2])][1] for m in cmp)]
 metrics={}
 for m in methods:
  bad=lambda p:maps[m][(p[0],p[1])][0]!=maps[m][(p[0],p[2])][0]
  full=sum(bad(p) or not maps[m][(p[0],p[1])][1] or not maps[m][(p[0],p[2])][1] for p in pairs)/len(pairs)
  groups=defaultdict(list)
  for p in common:groups[p[0]].append(bad(p))
  metrics[m]={'tsr':1-len(fail[m])/160,'failed_ids':fail[m],'common_pair_weighted_flip':sum(bad(p) for p in common)/len(common),'common_group_macro_flip':sum(sum(v)/len(v) for v in groups.values())/len(groups),'all_pair_flip_or_failure':full}
 result['runs'][name]={'checks':checks,'n_common_pairs':len(common),'n_all_pairs':len(pairs),'metrics':metrics}
Path(__file__).with_name('checks.json').write_text(json.dumps(result,indent=2)+'\n')
for name,r in result['runs'].items():print(name,r['checks'],r['n_common_pairs'],{m:r['metrics'][m] for m in ['B0','B6','darc_selected','b4_selected']})
print('overlap old E2',result['overlap_old_e2'])
