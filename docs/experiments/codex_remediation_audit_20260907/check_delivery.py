from pathlib import Path
from collections import Counter
import json,os,subprocess,shutil,tempfile
ROOT=Path.cwd();CORE=ROOT/'9-AutoDriving-core';AUDIT=ROOT/'docs/experiments/codex_remediation_audit_20260907';env=dict(os.environ,PYTHONPATH=str(CORE))
cli=[str(CORE/'.venv/bin/python'),str(CORE/'scripts/experiment.py'),'replay']
run=CORE/'results/runs/20260906T051339Z_main_test'
results={}
p=subprocess.run(cli,env=env,capture_output=True,text=True);(AUDIT/'requested_replay.txt').write_text(p.stdout+p.stderr);results['default_replay_exit']=p.returncode;print('default replay',p.returncode,flush=True)
for name,mutate in [('missing_159_groups_and_summary',False),('missing_cached_candidates_routes',True)]:
 with tempfile.TemporaryDirectory() as td:
  path=Path(td);shutil.copy2(run/'test_001_graph.json',path/'test_001_graph.json');d=json.loads((run/'test_001.json').read_text())
  if mutate:
   for u in d['utterances']:u['candidates']={};u['routes']={}
  (path/'test_001.json').write_text(json.dumps(d));p=subprocess.run(cli+['--run-dir',td,'--output-dir',str(AUDIT/name/'out')],env=env,capture_output=True,text=True)
  results[name]={'exit':p.returncode,'output':p.stdout+p.stderr};print(name,p.returncode,flush=True)
data=json.loads((CORE/'data/test/test_640_utterances.json').read_text());lookup={u['utterance_id']:u for u in data};diff=[];wdiff=[]
for f in sorted(run.glob('test_*.json')):
 if f.name.endswith('_graph.json'):continue
 for u in json.loads(f.read_text())['utterances']:
  if u['text']!=lookup[u['utterance_id']]['text']:diff.append(u['utterance_id'])
  if u['gold_intent']['quality_weight']!=lookup[u['utterance_id']]['w_synthetic']:wdiff.append(u['utterance_id'])
results['changed_text_vs_cached']=diff;results['changed_weight_vs_cached']=wdiff
for name in ['pilot/pilot_80_utterances.json','pilot/annotation_pilot_80_review_queue.json','test/annotation_test_640_review_queue.json']:
 d=json.loads((CORE/'data'/name).read_text());results[name]={'count':len(d),'statuses':dict(Counter(x.get('annotation_status','missing') for x in d))}
splits=json.loads((CORE/'data/processed/candidate_splits.json').read_text());exp=json.loads((CORE/'data/processed/development_exposure.json').read_text());results['actual_split_keys']=list(splits);results['actual_exposure_keys']=list(exp)
from sys import path as syspath
syspath.insert(0,str(CORE))
from scripts.run_pilot_gate_admission import audit_splits_leakage
results['gate_leakage_function']=audit_splits_leakage()
(AUDIT/'delivery_checks.json').write_text(json.dumps(results,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in results.items() if not isinstance(v,list) and not k.startswith('missing_')},ensure_ascii=False),flush=True)
# Restore report files overwritten by the commands, retaining generated evidence.
generated=AUDIT/'reports_generated_by_audit';generated.mkdir(exist_ok=True)
for before in (AUDIT/'reports_before').iterdir():
 if not before.is_file():continue
 current=CORE/'results/reports'/before.name
 if current.is_file() and current.read_bytes()!=before.read_bytes():
  shutil.copy2(current,generated/current.name);shutil.copy2(before,current)
