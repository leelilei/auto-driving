"""Offline planning of one saved predicted intent. Does not load benchmark gold."""
import argparse
import contextlib
import copy
import json
import time
from pathlib import Path

import chinatravel_pipeline_v3 as ct
import chinatravel_parse_plan_v4 as parser
from chinatravel_ready_backend_v3 import ConstraintAwareAgent, requirements
from chinatravel_symbolic_backend import TracedWorldEnv, NoModel
from run_chinatravel_readiness_v3 import native, write


def run(request, out, seconds=30):
    out.mkdir(parents=True, exist_ok=False)
    write(out/'request.json', request)
    intent=request.get('parsed_intent')
    result={'status':'INVALID_INTENT', 'new_model_calls':0,
            'officially_evaluated':False, 'seconds_limit':seconds}
    try:
        parser.validate(intent, request['nature_language'])
    except (ValueError, TypeError, KeyError) as exc:
        result['error_type']=type(exc).__name__
    else:
        result.update(requirements(intent))
        if result['status']=='READY_TO_PLAN':
            q={k:intent[k] for k in ('start_city','target_city','days','people_number')}
            q.update(uid='local_request', hard_logic_py=parser.compile_extended(intent))
            write(out/'predicted_constraints.json', q)
            start=time.monotonic()
            with ct.offline(), (out/'search.log').open('w') as log, (out/'tool_trace.jsonl').open('w') as trace, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                try:
                    env=TracedWorldEnv(trace)
                    agent=ConstraintAwareAgent(intent=intent,env=env,backbone_llm=NoModel(),cache_dir=str(out/'cache'),log_dir=str(out/'logs'),search_width=10,debug=False)
                    agent.TIME_CUT=seconds
                    with ct.deadline(seconds):
                        success, plan=agent.symbolic_search(copy.deepcopy(q))
                    plan=native(plan)
                    result['status']='PLAN_FOUND' if success and ct.valid_plan(plan) else 'SEARCH_FAILED'
                    write(out/'candidate.json', plan)
                except Exception as exc:
                    result.update(status='SEARCH_ERROR', error_type=type(exc).__name__)
            result['elapsed_seconds']=time.monotonic()-start
    write(out/'result.json', result)
    write(out/'hashes.json',{str(p.relative_to(out)):ct.sha(p) for p in out.rglob('*') if p.is_file()})
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=30)
    a=p.parse_args()
    if not 1<=a.seconds<=300:p.error('--seconds must be 1..300')
    result=run(json.loads(a.request.read_text()),a.out.resolve(),a.seconds)
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['status'] in ('PLAN_FOUND','NEEDS_CLARIFICATION') else 2)
