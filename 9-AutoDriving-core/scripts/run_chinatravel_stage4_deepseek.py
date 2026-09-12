"""Offline planning for DeepSeek's contract-valid subset."""
import contextlib,copy,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'; OUT=RUN/'stage4_deepseek_planning'
def main():
 import sys;sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'));import chinatravel_parse_plan_v4 as v4,chinatravel_pipeline_v3 as ct
 from chinatravel_symbolic_backend import MealStateRuleAgent,TracedWorldEnv,NoModel
 src=json.loads((RUN/'collection_deepseek_report.json').read_text());public={x['uid']:x['nature_language'] for x in json.loads((RUN/'public_inputs.json').read_text())};OUT.mkdir(exist_ok=False); rows=[]
 for r in src['records']:
  if r['status']!='JSON_VALID': continue
  p=r['parsed_intent']
  try:v4.validate(p,public[r['uid']]);v4.compile_extended(p)
  except Exception as e: rows.append({'uid':r['uid'],'status':'contract_failure','error':str(e)});continue
  d=OUT/r['uid'];d.mkdir();q={k:p[k] for k in ('start_city','target_city','days','people_number')};q.update(uid=r['uid'],hard_logic_py=v4.compile_extended(p));ct.write(d/'intent.json',p);ct.write(d/'compiled_query.json',q);started=time.monotonic();plan={};success=False
  with (d/'search.log').open('w') as log,(d/'tool_trace.jsonl').open('w') as trace,ct.offline(),contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
   env=TracedWorldEnv(trace);agent=MealStateRuleAgent(env=env,backbone_llm=NoModel(),cache_dir=str(d/'cache'),log_dir=str(d/'logs'),search_width=10,debug=False);agent.TIME_CUT=30
   try:
    with ct.deadline(30):success,plan=agent.symbolic_search(copy.deepcopy(q))
    status='search_success' if success else 'search_failed'
   except Exception as e:status='search_error:'+type(e).__name__; (d/'error.txt').write_text(str(e))
  ct.write(d/'raw_search_return.json',plan);s={'uid':r['uid'],'status':status,'seconds':time.monotonic()-started,'tool_calls':len(env.results),'tool_errors':sum(not x['success'] for x in env.results),'schema_valid':ct.valid_plan(plan)};ct.write(d/'summary.json',s);rows.append(s)
 result={'status':'DEEPSEEK_STAGE4_PLANNING_COMPLETE','model_api_calls':0,'cases':rows,'semantic_error_candidates':[]};ct.write(OUT/'summary.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
