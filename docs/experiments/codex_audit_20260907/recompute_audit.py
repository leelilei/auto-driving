"""Read-only audit of existing runs. No API calls; only output is audit JSON."""
from pathlib import Path
import sys,json
from collections import Counter
ROOT=Path(__file__).resolve().parents[3]
CORE=ROOT/'9-AutoDriving-core';sys.path.insert(0,str(CORE))
from scripts.collect_b1_test import evaluate_method_on_test
from src.graph import SyntheticGraph
out={}
for run in sorted((CORE/'results/runs').glob('*main_test*')):
 groups=[json.loads(p.read_text()) for p in sorted(run.glob('test_*.json')) if not p.name.endswith('_graph.json')]
 if not groups:continue
 flat=[u for g in groups for u in g['utterances']]
 calls=[c for u in flat for c in u['calls'].values()]
 info={'groups':len(groups),'utterances':len(flat),'stored_call_records':len(calls),'transport_error_records':sum('transport_error_type' in c for c in calls),'schema_valid_records':sum(c.get('schema_valid',False) for c in calls),'missing_preference_direction':sum('preference_direction' not in u for u in flat),'methods':{}}
 if run.name.endswith('_main_test'):
  graphs={g['group_id']:SyntheticGraph.load(run/f"{g['group_id']}_graph.json") for g in groups}
  cfg=json.loads((CORE/'data/calibration/frozen_config.json').read_text())['calibrated_parameters']
  for method in ['B0','B1','B2','B3','B4','B5','B6','Ours']:
   res=evaluate_method_on_test(flat,graphs,method,tau=cfg['tau_star'],tau_sem=cfg['tau_sem_star'],p_review=cfg['p_review_star'])
   info['methods'][method]={k:v for k,v in res.items() if k!='eval_records'}
 out[run.name]=info
 print(run.name,json.dumps(info,ensure_ascii=False),flush=True)
q=CORE/'data/test/annotation_test_640_review_queue.json'
out['test_annotation_queue']=dict(Counter(x.get('annotation_status','missing') for x in json.loads(q.read_text())))
out['repeat_artifacts']={str(p.relative_to(CORE)):len(list(p.glob('test_*.json'))) for p in (CORE/'results/runs').glob('*ablation/repeat_run_*')}
(Path(__file__).parent/'recomputed_run_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
