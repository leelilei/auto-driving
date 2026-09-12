"""Offline predicted-intent -> official RuleNeSy interface probe, without gold or LLMs.

This narrow JSON compiler supports city/day/party/budget only. It is NOT a full
ChinaTravel semantic parser or an effectiveness experiment.
"""
import argparse
import contextlib
import copy
import io
import math
from pathlib import Path
import sys
import time

import chinatravel_pipeline_v3 as ct


def compile_intent(intent):
    from chinatravel.environment.language import city_names
    if set(intent)!={'start_city','target_city','days','people_number','budget'}:
        raise ValueError('Supported fields: start_city,target_city,days,people_number,budget only')
    for key in ('start_city','target_city'):
        if intent[key] not in city_names('zh'):raise ValueError('Unsupported city')
    if intent['start_city']==intent['target_city']:raise ValueError('Distinct cities required')
    for key in ('days','people_number'):
        if type(intent[key]) is not int or intent[key]<1:raise ValueError('Positive integer required: '+key)
    budget=intent['budget']
    if type(budget) not in (int,float) or not math.isfinite(budget) or budget<0:
        raise ValueError('Finite nonnegative numeric budget required')
    return [f"result = (day_count(plan) == {intent['days']})",
            f"result = (people_count(plan) == {intent['people_number']})",
            'total = 0\nfor activity in allactivities(plan):\n    total += activity_cost(activity)\n    total += innercity_transport_cost(activity_transports(activity))\n'+f'result = (total <= {budget!r})']


class NoModel:
    name='offline_predicted_intent'
    def __call__(self,*args,**kwargs):raise AssertionError('No LLM is allowed in symbolic probe')


def solve(intent,directory,seconds=30):
    # Upstream NL2SL module loads its static check plans relative to repository cwd.
    with contextlib.chdir(ct.UPSTREAM):
        from chinatravel.agent.nesy_agent.rule_driven_rec import RuleDrivenAgent
    from chinatravel.environment.world_env import WorldEnv
    from chinatravel.symbol_verification.hard_constraint import evaluate_constraints_py
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=False)
    constraints=compile_intent(intent)
    query={key:value for key,value in intent.items() if key!='budget'}
    query.update(uid=directory.name,hard_logic_py=constraints)
    ct.write(directory/'predicted_intent.json',intent)
    ct.write(directory/'compiled_query.json',query)
    started=time.monotonic();plan={};search_success=False;status='not_started'
    with (directory/'search.log').open('w') as log,ct.offline(),contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        env=WorldEnv(lang='zh')
        agent=RuleDrivenAgent(env=env,backbone_llm=NoModel(),cache_dir=str(directory/'cache'),
                              log_dir=str(directory/'logs'),search_width=10,debug=False)
        agent.TIME_CUT=seconds
        try:
            with ct.deadline(max(0.01,seconds-(time.monotonic()-started))):
                search_success,plan=agent.symbolic_search(copy.deepcopy(query))
            status='search_success' if search_success else 'search_failed'
        except Exception as exc:
            status='search_error:'+type(exc).__name__
        raw_plan=copy.deepcopy(plan)
        # Expose upstream's best-so-far separately; never pass it off as search success.
        best=getattr(agent,'least_plan_logic',None) or getattr(agent,'least_plan_comm',None) or getattr(agent,'least_plan_schema',None) or {}
        candidate=raw_plan if ct.valid_plan(raw_plan) else best
        local_score=ct.json_safe(ct.v1.evaluate({query['uid']:query},{query['uid']:candidate}))
        local_constraints=evaluate_constraints_py(constraints,candidate) if ct.valid_plan(candidate) else []
    ct.write(directory/'raw_search_return.json',raw_plan)
    ct.write(directory/'best_so_far.json',best)
    ct.write(directory/'candidate.json',candidate)
    ct.write(directory/'predicted_constraint_score.json',local_score)
    summary={'status':status,'search_success':bool(search_success),'seconds':time.monotonic()-started,
        'candidate_origin':'raw_search_return' if ct.valid_plan(raw_plan) else 'explicit_best_so_far',
        'schema_valid':ct.valid_plan(candidate),'tool_calls':len(env.results),
        'tool_errors':sum(not result['success'] for result in env.results),'search_nodes':getattr(agent,'search_nodes',0),
        'candidate_constraint_pass':list(map(bool,local_constraints)),
        'predicted_all_pass_rate':local_score['all_pass_rate'],
        'scope':'constructed predicted-intent interface diagnostic; no gold; no natural model errors; no effectiveness claim'}
    ct.write(directory/'summary.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out',required=True)
    args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    cases=[{'name':'public_requirements_1500','intent':{'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':1500}},
           {'name':'constructed_budget_10','intent':{'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':10}}]
    ct.write(out/'plan.json',{'scope':'offline interface diagnostic, deliberately constructed budget contrast',
        'cases':cases,'search_width':10,'seconds_per_case':30,'model_calls':0,
        'source_hashes':{**ct.source_hashes(),str(Path(__file__).resolve().relative_to(ct.ROOT)):ct.sha(__file__)}})
    results={case['name']:solve(case['intent'],out/case['name']) for case in cases}
    ct.write(out/'summary.json',results)
    print(ct.dumps(results))


if __name__=='__main__':main()
