import sys,json,copy,tempfile,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[4]/'9-AutoDriving-core';sys.path.insert(0,str(R))
from scripts.unified_evaluator import load_run_data,evaluate_cohort
p=R/'results/runs/20260912T074558Z_e2_confirmation_gpt-5_6-luna'
u,g=load_run_data(p);out={}
x=copy.deepcopy(u[:4]);q=json.loads(x[0]['calls']['review']['user_prompt']);q['instruction']='different instruction';x[0]['calls']['review']['user_prompt']=json.dumps(q)
r=evaluate_cohort(x,g,'instruction_tampered');out['changed_instruction_accepted']={'candidate_match_count':r['audit_checks']['candidate_match_count'],'n':r['utterances_count']}
with tempfile.TemporaryDirectory() as t:
 t=Path(t)
 for f in p.glob('e2_clean_*.json'):shutil.copy2(f,t/f.name)
 (t/'e2_clean_040.json').unlink();(t/'e2_clean_040_graph.json').unlink()
 a,b=load_run_data(t);r=evaluate_cohort(a,b,'missing_group');out['deleted_group_accepted']={'n':len(a),'groups':len(b),'evaluated':r['groups_count']}
src=Path(__file__).parents[1]/'unified_audit_metrics.json';new=Path(__file__).with_name('recomputed.json');out['recomputed_json_equal']=json.loads(src.read_text())==json.loads(new.read_text())
Path(__file__).with_name('probe.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
