"""Explicit host capability routing over an archived native parse; no new LLM call.

Only a whole generic request to produce a travel plan can be fulfilled by the
planner itself. Concrete travel constraints remain unresolved and stop execution.
"""
import argparse
import contextlib
import io
from pathlib import Path
import re
import shutil

import chinatravel_parse_plan as parent
from chinatravel_symbolic_backend import solve
ct=parent.ct

POLICY={'version':'output_request_routing_v1',
        'rule':'full string generic plan request, optional generic explanatory parenthesis; base phrase must occur verbatim in original query',
        'preservation':'raw native parse unchanged; resolution records separate; concrete constraints never removed',
        'model_calls':0,'search_seconds':30,'search_width':10}
REQUEST=re.compile(r'(?P<base>请(?:给|为)我(?:一个|一份)?(?:旅行|旅游|行程)(?:规划|计划|安排))(?:[（(](?:具体)?行程规划[）)])?[。！!]?')


def route(parsed,original):
    resolutions=[];unresolved=[]
    for item in parsed['unsupported_requirements']:
        match=REQUEST.fullmatch(item)
        if match and match.group('base') in original:
            resolutions.append({'raw_requirement':item,'original_evidence':match.group('base'),
                                'handled_by':'RuleNeSy itinerary generation, not an additional itinerary constraint'})
        else:unresolved.append(item)
    return {'resolved_by_planner':resolutions,'unresolved_requirements':unresolved,
            'intent':{key:parsed[key] for key in parent.FIELDS},'policy':POLICY}


def pins():
    extra=[Path(__file__),ct.CORE/'tests/test_chinatravel_parse_plan_v2.py']
    return {**parent.pins(),**{str(path.resolve().relative_to(ct.ROOT)):ct.sha(path) for path in extra}}


def score(out):
    uid=ct.read(out/'plan.json')['uid']
    with ct.offline(),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        return ct.json_safe(ct.v1.evaluate({uid:parent.evaluation_query(uid)},ct.read(out/'predictions.json')))


def run(source,out):
    parent.replay(source)
    public=ct.read(source/'public_inputs.json')[0]
    raw=ct.read(source/'parsed_intent.json')
    out.mkdir(parents=True,exist_ok=False)
    for name in ('request.json','public_inputs.json','parsed_intent.json'):
        shutil.copy2(source/name,out/name)
    ct.write(out/'plan.json',{'adapter':'native_parse_RuleNeSy_output_request_routing_v2','uid':public['uid'],
        'parent_run':str(source),'parent_manifest_sha256':ct.sha(source/'manifest_hashes.json'),
        'scope':'offline continuation of one real model parse; not an independent model sample or fresh retry',
        'new_physical_requests':0,'inherited_unique_model_requests':1,'policy':POLICY,'source_hashes':pins(),
        'fixed_input_hashes':{name:ct.sha(out/name) for name in ('request.json','public_inputs.json','parsed_intent.json')}})
    resolution=route(raw,public['nature_language'])
    ct.write(out/'capability_resolution.json',resolution)
    prediction={};summary={'status':'unresolved_requirements'}
    if not resolution['unresolved_requirements'] and all(value is not None for value in resolution['intent'].values()):
        prediction,summary=solve(resolution['intent'],out/'search')
    ct.write(out/'predictions.json',{public['uid']:prediction})
    ct.write(out/'collection.json',{'new_physical_requests':0,'inherited_unique_model_requests':1,'search':summary})
    ct.write(out/'official_score.json',score(out))
    ct.write(out/'manifest_hashes.json',{str(path.relative_to(out)):ct.sha(path) for path in sorted(out.rglob('*')) if path.is_file()})
    return replay(out)


def replay(out):
    with ct.offline():
        plan=ct.read(out/'plan.json');hashes=ct.read(out/'manifest_hashes.json')
        if plan['source_hashes']!=pins():raise ValueError('Source integrity failure')
        required={'plan.json','public_inputs.json','request.json','parsed_intent.json','capability_resolution.json',
                  'predictions.json','collection.json','official_score.json'}
        if not required<=set(hashes):raise ValueError('Required roles missing')
        inventory={str(path.relative_to(out)) for path in out.rglob('*') if path.is_file()}-{'manifest_hashes.json','replay_report.json'}
        if set(hashes)!=inventory:raise ValueError('Artifact inventory mismatch')
        for name,digest in hashes.items():
            if ct.sha(out/name)!=digest:raise ValueError('Artifact integrity failure: '+name)
        for name,digest in plan['fixed_input_hashes'].items():
            if ct.sha(out/name)!=digest:raise ValueError('Frozen input changed')
        source=Path(plan['parent_run'])
        if ct.sha(source/'manifest_hashes.json')!=plan['parent_manifest_sha256']:raise ValueError('Parent archive changed')
        parent.replay(source)
        for name in plan['fixed_input_hashes']:
            if ct.sha(out/name)!=ct.sha(source/name):raise ValueError('Inherited model evidence differs from parent')
        public=ct.read(out/'public_inputs.json')[0];raw=ct.read(out/'parsed_intent.json')
        if route(raw,public['nature_language'])!=ct.read(out/'capability_resolution.json'):raise ValueError('Capability routing mismatch')
        prediction=ct.read(out/'predictions.json')
        if set(prediction)!={plan['uid']}:raise ValueError('Prediction IDs mismatch')
        collection=ct.read(out/'collection.json')
        if collection['new_physical_requests']!=0:raise ValueError('Unexpected new model calls')
        if collection['search']['status']=='search_success':
            if prediction[plan['uid']]!=ct.read(out/'search/raw_search_return.json'):raise ValueError('Plan postprocessing detected')
            lines=(out/'search/tool_trace.jsonl').read_text().splitlines()
            if len(lines)!=collection['search']['tool_calls']:raise ValueError('Tool call count mismatch')
            if [ct.strict_json(line)['index'] for line in lines]!=list(range(1,len(lines)+1)):raise ValueError('Tool trace indices mismatch')
        elif prediction[plan['uid']]!={}:raise ValueError('Unexpected fallback prediction')
        official=score(out)
        if official!=ct.read(out/'official_score.json'):raise ValueError('Official score mismatch')
        report={'status':'PASS','offline':True,'score_identical':True,'new_physical_requests':0,
            'inherited_unique_model_requests':1,'schema_rate':official['schema_rate'],
            'commonsense_macro':official['commonsense_macro'],'hard_macro':official['hard_macro'],
            'all_pass_rate':official['all_pass_rate'],'n_expected':official['n_expected']}
        ct.write(out/'replay_report.json',report)
        return report


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('command',choices=['run','replay'])
    parser.add_argument('--source-run');parser.add_argument('--run-dir',required=True)
    args=parser.parse_args();out=Path(args.run_dir).resolve()
    if args.command=='run':
        if not args.source_run:parser.error('--source-run is required for offline continuation')
        result=run(Path(args.source_run).resolve(),out)
    else:result=replay(out)
    print(ct.dumps(result))


if __name__=='__main__':main()
