"""Bounded native intent parsing -> meal-state-corrected RuleNeSy -> official score.

One explicitly exposed dev regression case; not a full benchmark or DARC result.
"""
import argparse
import contextlib
from dataclasses import asdict
import io
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import urllib.error

import jsonschema
import chinatravel_pipeline_v3 as ct

SYSTEM='Extract explicit travel requirements from the complete original query. Call parse_intent once. Do not plan an itinerary. Never invent requirements or silently drop unsupported clauses.'
INSTRUCTION=('请完整读取原句。只提取起点城市、目标城市、天数、人数、总预算，调用 parse_intent。'
    '城市用中文。每个字段提供原句中的依据片段；缺失或不明确的字段为 null，依据用空串。'
    '五个字段以外的具体要求，或存在歧义的要求，逐条保留在 unsupported_requirements，不能自行忽略。')
FIELDS=('start_city','target_city','days','people_number','budget')


def tool_spec():
    from chinatravel.environment.language import city_names
    properties={'start_city':{'type':['string','null'],'enum':city_names('zh')+[None]},
        'target_city':{'type':['string','null'],'enum':city_names('zh')+[None]},
        'days':{'type':['integer','null'],'minimum':1},'people_number':{'type':['integer','null'],'minimum':1},
        'budget':{'type':['number','null'],'minimum':0},
        'evidence':{'type':'object','properties':{key:{'type':'string'} for key in FIELDS},'required':list(FIELDS),'additionalProperties':False},
        'unsupported_requirements':{'type':'array','items':{'type':'string'}}}
    return {'tools':[{'name':'parse_intent','description':'Extract supported fields and quote their source evidence; flag all unsupported requirements.',
        'input_schema':{'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}}],
        'tool_choice':{'type':'tool','name':'parse_intent','disable_parallel_tool_use':True}}


def decode(data,public):
    blocks=[b for b in data.get('content',[]) if b.get('type')=='tool_use']
    if len(blocks)!=1 or blocks[0].get('name')!='parse_intent' or data.get('stop_reason')!='tool_use':
        raise ValueError('Expected one complete parse_intent native tool call')
    value=blocks[0].get('input')
    jsonschema.Draft7Validator(tool_spec()['tools'][0]['input_schema']).validate(value)
    for key in FIELDS:
        evidence=value['evidence'][key]
        if value[key] is not None and (not evidence or evidence not in public['nature_language']):
            raise ValueError('Missing/nonverbatim evidence for '+key)
    return value


def payload(public):
    from llm_client import resolve_config
    config=resolve_config(ct.CONFIG)
    user=ct.dumps({'task':public,'instruction':INSTRUCTION})
    return {'model':config.model,'system':SYSTEM,'messages':[{'role':'user','content':user}],
        'temperature':0.0,'max_tokens':4096,**tool_spec()}


def pins():
    files=[Path(__file__),ct.CORE/'scripts/chinatravel_symbolic_backend.py',ct.CORE/'scripts/chinatravel_symbolic_probe.py',
           ct.CORE/'tests/test_chinatravel_symbolic_backend.py',ct.CORE/'tests/test_chinatravel_parse_plan.py']
    files.extend((ct.UPSTREAM/'chinatravel/data/dev_split').glob('*.json'))
    return {**ct.source_hashes(),**{str(p.resolve().relative_to(ct.ROOT)):ct.sha(p) for p in files}}


def evaluation_query(uid):
    merged=ct.read(ct.DATA)[uid]
    canonical=ct.read(ct.UPSTREAM/'chinatravel/data/dev_split'/f'{uid}.json')
    for key in ('uid','nature_language','hard_logic_py','target_city','days','people_number'):
        if canonical[key]!=merged[key]:raise ValueError('Original/merged query mismatch: '+key)
    if canonical['start_city']!=merged['org']:raise ValueError('Origin alias mismatch')
    return canonical


def verify(out):
    plan=ct.read(out/'plan.json')
    if plan['source_hashes']!=pins():raise ValueError('Source/config/data changed')
    if plan['public_sha256']!=ct.sha(out/'public_inputs.json'):raise ValueError('Public input changed')
    ct.v1.preflight()
    return plan


def prepare(out):
    from llm_client import resolve_config
    original=ct.read(ct.DATA)[ct.REGRESSION]
    public=ct.v1.model_input(original)
    out.mkdir(parents=True,exist_ok=False)
    ct.write(out/'public_inputs.json',[public])
    ct.v1.preflight()
    ct.write(out/'plan.json',{'adapter':'native_parse_RuleNeSy_meal_state_v1','ids':[public['uid']],
        'scope':'one exposed dev regression; city/day/party/budget interface only; unsupported requirements stop',
        'config':asdict(resolve_config(ct.CONFIG)),'max_physical_requests':1,'retries':0,'timeout':60,
        'max_output_tokens':4096,'max_request_chars_including_tools':50000,'search_seconds':30,'search_width':10,
        'expansion':'none; no second or third case in this narrow interface probe',
        'evaluation_input':'original dev_split JSON; merged org alias checked against original start_city; gold byte content unchanged',
        'system':SYSTEM,'instruction':INSTRUCTION,'tools':tool_spec(),'source_hashes':pins(),
        'public_sha256':ct.sha(out/'public_inputs.json'),
        'prior_this_session':'Act native v3 used 9 requests and failed; not merged into this result or hidden',
        'total_session_request_ceiling':10})
    ct.write(out/'predictions.json',{public['uid']:{}})


def collect(out):
    from llm_client import get_api_key,resolve_config
    verify(out)
    if (out/'request.json').exists() or (out/'collection.json').exists():raise ValueError('Case already attempted')
    public=ct.read(out/'public_inputs.json')[0]
    config=resolve_config(ct.CONFIG)
    body=payload(public)
    charged=len(body['system'])+len(body['messages'][0]['content'])+len(ct.dumps(tool_spec()))
    if charged>50000:raise ValueError('Request character budget exceeded')
    record={'uid':public['uid'],'call':1,'wire_payload':body,'charged_chars':charged,
            'input_chars':len(body['system'])+len(body['messages'][0]['content']),'timeout_seconds':60}
    ct.write(out/'request.json',record)
    started=time.monotonic();prediction={};status='not_started';search=None
    try:
        key=get_api_key(config.provider,config.api_key_env)
        request=urllib.request.Request(config.base_url.rstrip('/')+'/v1/messages',method='POST',data=ct.dumps(body).encode(),
            headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json','User-Agent':'Mozilla/5.0'})
        with ct.deadline(60):
            with urllib.request.urlopen(request,timeout=60) as response:
                record['provider_response']=ct.strict_json(response.read().decode())
        record['request_seconds']=time.monotonic()-started
        ct.write(out/'request.json',record)
        extracted=decode(record['provider_response'],public)
        ct.write(out/'parsed_intent.json',extracted)
        if extracted['unsupported_requirements'] or any(extracted[key] is None for key in FIELDS):
            status='unsupported_or_incomplete_intent'
        else:
            from chinatravel_symbolic_backend import solve
            prediction,search=solve({key:extracted[key] for key in FIELDS},out/'search')
            status=search['status']
    except Exception as exc:
        status='error:'+type(exc).__name__
        record['error_type']=type(exc).__name__
        if isinstance(exc,urllib.error.HTTPError):record['http_status']=exc.code
        ct.write(out/'request.json',record)
    ct.write(out/'predictions.json',{public['uid']:prediction})
    ct.write(out/'collection.json',{'uid':public['uid'],'status':status,'physical_requests':1,'chars':charged,
        'elapsed_seconds':time.monotonic()-started,'search':search})


def score(out):
    frozen=verify(out)
    predictions=ct.read(out/'predictions.json')
    if set(predictions)!=set(frozen['ids']):raise ValueError('Prediction IDs differ from plan')
    with ct.offline(),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        return ct.json_safe(ct.v1.evaluate({uid:evaluation_query(uid) for uid in frozen['ids']},predictions))


def seal(out):
    ct.write(out/'official_score.json',score(out))
    ct.write(out/'manifest_hashes.json',{str(path.relative_to(out)):ct.sha(path) for path in sorted(out.rglob('*')) if path.is_file()})


def replay(out):
    with ct.offline():
        frozen=verify(out)
        hashes=ct.read(out/'manifest_hashes.json')
        required={'plan.json','public_inputs.json','request.json','collection.json','predictions.json','official_score.json'}
        if not required<=set(hashes):raise ValueError('Required artifact roles missing')
        actual={str(path.relative_to(out)) for path in out.rglob('*') if path.is_file()}-{'manifest_hashes.json','replay_report.json'}
        if actual!=set(hashes):raise ValueError('File inventory changed')
        for name,digest in hashes.items():
            if ct.sha(out/name)!=digest:raise ValueError('Artifact integrity failure: '+name)
        record=ct.read(out/'request.json');public=ct.read(out/'public_inputs.json')[0]
        collection=ct.read(out/'collection.json')
        if record['wire_payload']!=payload(public) or record['call']!=1 or collection['physical_requests']!=1:
            raise ValueError('Request identity/content mismatch')
        expected_chars=len(SYSTEM)+len(record['wire_payload']['messages'][0]['content'])+len(ct.dumps(tool_spec()))
        if record['charged_chars']!=expected_chars or collection['chars']!=expected_chars or expected_chars>50000:
            raise ValueError('Request budget mismatch')
        if (out/'parsed_intent.json').exists():
            extracted=decode(record['provider_response'],public)
            if extracted!=ct.read(out/'parsed_intent.json'):raise ValueError('Native response/intent mismatch')
        predictions=ct.read(out/'predictions.json')
        if collection['status']=='search_success':
            if predictions[public['uid']]!=ct.read(out/'search/raw_search_return.json'):
                raise ValueError('Prediction differs from raw search return')
        elif predictions[public['uid']]!={}:raise ValueError('Failure must not use a fallback prediction')
        official=score(out)
        if official!=ct.read(out/'official_score.json'):raise ValueError('Official score mismatch')
        usage=record.get('provider_response',{}).get('usage',{})
        report={'status':'PASS','offline':True,'score_identical':True,'physical_requests':1,
            'provider_input_tokens':usage.get('input_tokens'),'provider_output_tokens':usage.get('output_tokens'),
            'all_pass_rate':official['all_pass_rate'],'n_expected':official['n_expected']}
        ct.write(out/'replay_report.json',report)
        return report


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('command',choices=['run','collect','replay'])
    parser.add_argument('--run-dir',required=True);args=parser.parse_args();out=Path(args.run_dir).resolve()
    if args.command=='collect':collect(out)
    elif args.command=='replay':print(ct.dumps(replay(out)))
    else:
        prepare(out)
        subprocess.run([sys.executable,__file__,'collect','--run-dir',str(out)],check=True)
        seal(out)
        print(ct.dumps(replay(out)))


if __name__=='__main__':main()
