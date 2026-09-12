"""Run offline RuleNeSy planning for the four normalized intents."""
import contextlib, copy, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'; OUT=RUN/'stage4_planning'
def main():
    import sys; sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
    import chinatravel_parse_plan_v4 as v4, chinatravel_pipeline_v3 as ct
    from chinatravel_symbolic_backend import MealStateRuleAgent, TracedWorldEnv, NoModel
    from chinatravel.symbol_verification.hard_constraint import evaluate_constraints_py
    data=json.loads((RUN/'stage4_json_attribution.json').read_text()); OUT.mkdir(exist_ok=False); summaries=[]
    for row in data['rows']:
        if row['attribution']!='planning_ready': continue
        uid=row['uid']; d=OUT/uid; d.mkdir(); intent=row['normalized_intent']; query={k:intent[k] for k in ('start_city','target_city','days','people_number')}; query.update(uid=uid,hard_logic_py=v4.compile_extended(intent)); ct.write(d/'normalized_intent.json',intent); ct.write(d/'compiled_query.json',query)
        started=time.monotonic(); plan={}; success=False
        with (d/'search.log').open('w') as log,(d/'tool_trace.jsonl').open('w') as trace,ct.offline(),contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            env=TracedWorldEnv(trace); agent=MealStateRuleAgent(env=env,backbone_llm=NoModel(),cache_dir=str(d/'cache'),log_dir=str(d/'logs'),search_width=10,debug=False); agent.TIME_CUT=30
            try:
                with ct.deadline(30): success,plan=agent.symbolic_search(copy.deepcopy(query))
                status='search_success' if success else 'search_failed'
            except Exception as e: status='search_error:'+type(e).__name__; (d/'error.txt').write_text(str(e))
        ct.write(d/'raw_search_return.json',plan)
        summary={'uid':uid,'status':status,'search_success':bool(success),'seconds':time.monotonic()-started,'tool_calls':len(env.results),'tool_errors':sum(not x['success'] for x in env.results),'schema_valid':ct.valid_plan(plan)}
        ct.write(d/'summary.json',summary); summaries.append(summary)
    result={'status':'STAGE4_PLANNING_COMPLETE','model_api_calls':0,'cases':summaries,'semantic_error_candidates':[]}
    ct.write(OUT/'summary.json',result); print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
