"""RuleNeSy local adapter: preserve meal state; never modify generated plans or gold."""
import contextlib
import copy
from pathlib import Path
import time

import chinatravel_pipeline_v3 as ct
from chinatravel_symbolic_probe import compile_intent, NoModel

with contextlib.chdir(ct.UPSTREAM):
    from chinatravel.agent.nesy_agent.rule_driven_rec import RuleDrivenAgent
from chinatravel.environment.world_env import WorldEnv


class TracedWorldEnv(WorldEnv):
    def __init__(self,trace):
        super().__init__(lang='zh')
        self.trace=trace

    def __call__(self,command):
        from pandas import DataFrame
        result=super().__call__(command)
        data=result['whole_data']
        if isinstance(data,DataFrame):
            data=ct.strict_json(data.to_json(orient='records',force_ascii=False))
        self.trace.write(ct.dumps({'index':len(self.results),'command':command,'success':result['success'],'observation':data})+'\n')
        return result


class MealStateRuleAgent(RuleDrivenAgent):
    def select_next_poi_type(self,candidates_type,plan,poi_plan,current_day,current_time,current_position):
        selected,candidates=super().select_next_poi_type(candidates_type,plan,poi_plan,current_day,current_time,current_position)
        eaten={activity['type'] for activity in plan[current_day]['activities'] if activity['type'] in ('lunch','dinner')}
        remaining=[kind for kind in candidates if kind not in eaten]
        if selected in eaten:
            # The upstream early meal branches return [meal] alone. Resume attraction
            # search when that meal is already present; ordinary return/hotel branches
            # and all upstream validity checks remain in force.
            return 'attraction',remaining or ['attraction']
        return selected,remaining


def solve(intent,directory,seconds=30):
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=False)
    query={key:value for key,value in intent.items() if key!='budget'}
    query.update(uid=directory.name,hard_logic_py=compile_intent(intent))
    ct.write(directory/'compiled_prediction.json',query)
    started=time.monotonic();plan={};status='not_started';success=False
    with (directory/'search.log').open('w') as log,(directory/'tool_trace.jsonl').open('w') as trace,ct.offline(),contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        env=TracedWorldEnv(trace)
        agent=MealStateRuleAgent(env=env,backbone_llm=NoModel(),cache_dir=str(directory/'cache'),
             log_dir=str(directory/'logs'),search_width=10,debug=False)
        agent.TIME_CUT=seconds
        try:
            with ct.deadline(max(0.01,seconds-(time.monotonic()-started))):
                success,plan=agent.symbolic_search(copy.deepcopy(query))
            status='search_success' if success else 'search_failed'
        except Exception as exc:
            status='search_error:'+type(exc).__name__
        best=getattr(agent,'least_plan_logic',None) or getattr(agent,'least_plan_comm',None) or getattr(agent,'least_plan_schema',None) or {}
    ct.write(directory/'raw_search_return.json',plan)
    ct.write(directory/'best_so_far_diagnostic_only.json',best)
    # No repair or best-so-far fallback enters predictions.
    prediction=plan if success and ct.valid_plan(plan) else {}
    summary={'status':status,'search_success':bool(success),'seconds':time.monotonic()-started,
             'tool_calls':len(env.results),'tool_errors':sum(not item['success'] for item in env.results),
             'search_nodes':getattr(agent,'search_nodes',0),'schema_valid':ct.valid_plan(prediction),
             'adapter':'RuleNeSy with meal-state correction; search_width=10; no plan postprocessing'}
    ct.write(directory/'summary.json',summary)
    return prediction,summary
