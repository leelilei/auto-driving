"""ChinaTravel Act JSON adapter v2: bounded development collection and offline replay."""
from __future__ import annotations

import argparse
import contextlib
from dataclasses import asdict
import io
import json
import math
import operator
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error
from unittest.mock import patch

import chinatravel_pipeline as v1

ROOT, CORE, UPSTREAM = v1.ROOT, v1.CORE, v1.UPSTREAM
read, write, sha, offline = v1.read, v1.write, v1.sha, v1.offline
DATA = CORE / 'data/chinatravel_dev_60.json'
CONFIG = CORE / 'configs/chinatravel_act_v2.json'
SCHEMA = UPSTREAM / 'chinatravel/evaluation/output_schema.json'
REGRESSION = 'e20241028160248698752'
BUDGET = dict(max_calls=12, query_calls=8, total_chars=160000, query_chars=110000,
              final_reserved_chars=50000, output_tokens=4096, timeout=60,
              seconds=900, retries=0, concurrency=1, consecutive_protocol_errors=2)
POLICY = dict(page_size=5, ordering='official returned order; no reranking',
              keys='all column/type pairs returned together; type objects converted to __name__',
              score_nulls='DataFrame NaN for non-applicable constraint columns serialized as null; scores unchanged',
              facts_chars=30000, retention='newest whole trace records fitting facts_chars; chronological order',
              raw_retention='all responses and full observations retained on disk',
              fences='strip exactly one outer ```json or ``` fence for actions only; never final output',
              final='one final request; no repair, fallback or scoring feedback')
SYSTEM = ('You plan travel using the REAL local ChinaTravel sandbox. Preserve every requirement in the '
          'complete original query. Only use queried facts; do not invent entities, schedules or prices. '
          'This is the Act JSON local protocol adapter, not native API function calling. '
          'Each query response must be exactly one JSON object: '
          '{"kind":"tool","name":"registered_name","arguments":{...}} or {"kind":"finish"}. '
          'No Python, lambda, expressions, multiple actions or prose. An optional single outer JSON fence is accepted. '
          'Use at most eight query requests, including errors; obtain outward and return transport, '
          'attractions, meals and connecting transport as needed. After queries a separate final request is provided. '
          'Unknown entity names must be resolved by querying attractions/restaurants/accommodations_select '
          'or poi_names; poi_lat_lon_search requires an exact name. '
          'Select filters are a list of {"key":column,"op":eq|ne|contains|lt|le|gt|ge,"value":scalar}; '
          'all conditions are ANDed, contains is literal string containment, no regex/OR/expressions. '
          'Omitted filters return all rows. page is zero-based, five rows per page in official order. '
          'Use keys tools to discover actual columns. Tools return explicit error categories. '
          'The supplied tool catalog defines required and optional arguments. ')
FINAL_SYSTEM = ('Return ONLY the final JSON object conforming to the supplied official schema; no Markdown '
                'or explanatory prose. Preserve the full original query and use queried facts. '
                'Do not fabricate unavailable facts. If you cannot produce a grounded plan return '
                '{"failure_reason":"explanation"}; this is recorded as schema failure. '
                'Plan round-trip travel with meals and attraction visits. Each activity.transports describes '
                'travel from the previous activity to this one. Use exact sandbox names. '
                'Include start/end and TrainID or FlightID on intercity activities; position on other activities. '
                'Include tickets for ticketed activities/metro, cars for taxi and rooms/room_type for accommodation. '
                'Transport price is per ticket/car and cost is total; walking price/cost are zero. '
                'The official goto observation cost is for the returned route; account for party size explicitly. ')

# The catalog is the entire model-callable surface. No model strings are executed.
CATALOG = {
    'intercity_transport_select': {'required': {'start_city':'str','end_city':'str','intercity_type':'str'},
                                  'optional': {'earliest_leave_time':'str','page':'int'}},
    'goto': {'required': {'city':'str','start':'str','end':'str','start_time':'str','transport_type':'str'}, 'optional': {}},
    'poi_lat_lon_search': {'required': {'city':'str','name':'str'}, 'optional': {}},
    'poi_names': {'required': {'city':'str'}, 'optional': {'contains':'str','page':'int'}},
}
for group in ('attractions', 'restaurants', 'accommodations'):
    CATALOG[group + '_keys'] = {'required': {'city':'str'}, 'optional': {}}
    CATALOG[group + '_select'] = {'required': {'city':'str'}, 'optional': {'filters':'list','page':'int'}}
    CATALOG[group + '_nearby'] = {'required': {'city':'str','point':'str'}, 'optional': {'topk':'int','dist':'number','page':'int'}}
for name in ('attractions_types', 'restaurants_cuisine'):
    CATALOG[name] = {'required': {'city':'str'}, 'optional': {'page':'int'}}
CATALOG['restaurants_with_recommended_food'] = {'required': {'city':'str','food':'str'}, 'optional': {'page':'int'}}


class ProtocolError(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(detail)


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def strict_json(raw):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('Duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    def constant(value):
        raise ValueError('Non-finite JSON value: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def parse_action(raw):
    text = raw.strip()
    conversion = 'none'
    match = re.fullmatch(r'```(?:json)?\s*\n(.*)\n```', text, re.DOTALL)
    if match:
        text, conversion = match.group(1), 'outer_markdown_fence'
    try:
        action = strict_json(text)
    except ValueError as exc:
        raise ProtocolError('invalid_json', str(exc)) from exc
    if not isinstance(action, dict):
        raise ProtocolError('multiple_or_non_object_actions', 'Exactly one action object is required')
    if action == {'kind':'finish'}:
        return action, conversion
    if action.get('kind') != 'tool':
        raise ProtocolError('unknown_kind', 'Expected tool or finish')
    if set(action) != {'kind', 'name', 'arguments'}:
        raise ProtocolError('invalid_action_fields', 'Expected exactly kind, name, arguments')
    return action, conversion


def typed(value, kind):
    if kind == 'number':
        return type(value) in (int,float) and math.isfinite(value)
    return type(value) is {'str':str, 'int':int, 'list':list}[kind]


class Sandbox:
    def __init__(self):
        from chinatravel.environment.world_env import WorldEnv
        self.env = WorldEnv(lang='zh')

    def dispatch(self, action):
        name, args = action.get('name'), action.get('arguments')
        if not isinstance(name, str) or name not in CATALOG:
            raise ProtocolError('unknown_tool', 'Tool is not registered')
        spec = CATALOG[name]
        if not isinstance(args, dict):
            raise ProtocolError('argument_type', 'arguments must be an object')
        if set(spec['required']) - set(args):
            raise ProtocolError('missing_argument', str(sorted(set(spec['required']) - set(args))))
        if set(args) - (set(spec['required']) | set(spec['optional'])):
            raise ProtocolError('unknown_argument', 'Only explicitly documented arguments are allowed')
        for key, value in args.items():
            if not typed(value, (spec['required'] | spec['optional'])[key]):
                raise ProtocolError('argument_type', key)
            if key in ('city','start_city','end_city') and value not in self.env.support_cities:
                raise ProtocolError('argument_value', 'Unsupported city: ' + value)
            if key in ('start_time','earliest_leave_time') and not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value):
                raise ProtocolError('argument_value', 'Time must be HH:MM in 00:00..23:59')
            if key in ('page','dist','topk') and (value < 0 or (key == 'topk' and value == 0)):
                raise ProtocolError('argument_value', key + ' out of range')
        for key, choices in [('transport_type', ('walk','taxi','metro')), ('intercity_type', ('train','airplane'))]:
            if key in args and args[key] not in choices:
                raise ProtocolError('argument_value', key + ' must be one of ' + str(choices))
        call = {'name':name, 'arguments':args, 'backend':'official bound method', 'prechecks':[]}
        kwargs = dict(args)
        page = kwargs.pop('page', 0)
        if name == 'goto' or name.endswith('_nearby') or name == 'poi_lat_lon_search':
            fields = ('start','end') if name == 'goto' else (('point',) if name.endswith('_nearby') else ('name',))
            for field in fields:
                value = self.env.poi.search(args['city'], args[field])
                call['prechecks'].append({'tool':'poi_lat_lon_search','city':args['city'],'name':args[field],'result':value})
                if isinstance(value, str):
                    return call, {'status':'unknown_entity','field':field,'name':args[field],
                                  'hint':'Query poi_names or the appropriate select tool; exact names required'}
        try:
            if name == 'poi_names':
                call['backend'] = 'public official Poi.data exact-name index (local adapter)'
                data = [n for n in self.env.poi.data[kwargs['city']] if kwargs.get('contains','') in n]
            elif name.endswith('_select') and name != 'intercity_transport_select':
                group = getattr(self.env, name.removesuffix('_select'))
                conditions = kwargs.pop('filters', [])
                predicates = self.predicates(conditions, group, kwargs['city'])
                # Each filter executes the official select, then intersects row indices.
                data = group.select(kwargs['city'], 'name', lambda x: True)
                for key, predicate in predicates:
                    subset = group.select(kwargs['city'], key, predicate)
                    data = data.loc[data.index.isin(subset.index)]
                call['predicate_policy'] = 'AND intersection of official select row indices; no eval'
            else:
                data = self.env._command_namespace()[name](**kwargs)
            if name.endswith('_keys'):
                return call, {'status':'ok', 'data':[[key,kind.__name__] for key,kind in data]}
            if isinstance(data, str):
                return call, {'status':'tool_internal_error','detail':data}
            return call, self.observe(data, page)
        except ProtocolError:
            raise
        except Exception as exc:
            return call, {'status':'tool_internal_error','error_type':type(exc).__name__, 'detail':str(exc)}

    def predicates(self, conditions, group, city):
        result = []
        ops = {'eq':operator.eq,'ne':operator.ne,'lt':operator.lt,'le':operator.le,'gt':operator.gt,'ge':operator.ge}
        for condition in conditions:
            if not isinstance(condition, dict) or set(condition) != {'key','op','value'}:
                raise ProtocolError('invalid_filter', 'Filter requires key, op, value')
            key, op, value = condition['key'], condition['op'], condition['value']
            if not isinstance(key, str) or key not in group.data[city].columns:
                raise ProtocolError('invalid_filter', 'Unknown column; query keys')
            if not isinstance(op, str) or op not in (*ops, 'contains') or type(value) not in (str,int,float,bool):
                raise ProtocolError('invalid_filter', 'Unsupported operator or non-scalar value')
            if op == 'contains':
                if not isinstance(value, str):
                    raise ProtocolError('invalid_filter', 'contains requires a string')
                predicate = lambda x, v=value: isinstance(x,str) and v in x
            else:
                fn = ops[op]
                def predicate(x, v=value, f=fn):
                    try:
                        return bool(f(x,v))
                    except (TypeError, ValueError) as exc:
                        raise ProtocolError('filter_type', 'Filter value does not match column type') from exc
            result.append((key,predicate))
        return result

    @staticmethod
    def observe(data, page):
        from pandas import DataFrame
        if isinstance(data, DataFrame):
            rows = json.loads(data.to_json(orient='records', force_ascii=False))
        elif hasattr(data, 'tolist'):
            rows = data.tolist()
        elif isinstance(data, (list,tuple)):
            rows = list(data)
        else:
            return {'status':'ok', 'data':data}
        start = page * POLICY['page_size']
        return {'status':'ok' if rows[start:start+5] else 'no_match', 'data':rows[start:start+5],
                'total_rows':len(rows), 'page':page, 'page_size':5,
                'next_page':page+1 if start+5 < len(rows) else None,
                'ordering':POLICY['ordering']}


def action_trace(raw, sandbox):
    trace = dict(raw_response=raw, parsed_action=None, dispatched_call=None, transformation='none')
    try:
        action, conversion = parse_action(raw)
        trace.update(parsed_action=action, transformation=conversion)
        if action['kind'] == 'finish':
            trace['observation'] = {'status':'finish'}
        else:
            trace['dispatched_call'], trace['observation'] = sandbox.dispatch(action)
    except ProtocolError as exc:
        trace['observation'] = {'status':'protocol_error','code':exc.code,'detail':str(exc)}
    return trace


def context(public, facts, phase):
    selected, used = [], 0
    for index in range(len(facts)-1, -1, -1):
        fact = {'trace_index':index, 'action':facts[index]['parsed_action'], 'observation':facts[index]['observation']}
        size = len(dumps(fact))
        if used + size <= POLICY['facts_chars']:
            selected.append(fact)
            used += size
    selected.reverse()
    obj = {'task':public, 'phase':phase, 'facts':selected,
           'omitted_trace_indices':[i for i in range(len(facts)) if i not in [f['trace_index'] for f in selected]]}
    if phase == 'final':
        obj['official_schema'] = read(SCHEMA)
    else:
        obj['tool_catalog'] = CATALOG
        obj['query_requests_remaining_after_this'] = max(0, BUDGET['query_calls']-len(facts)-1)
    return (FINAL_SYSTEM if phase == 'final' else SYSTEM).strip(), dumps(obj)


class BudgetStop(RuntimeError):
    pass


@contextlib.contextmanager
def deadline(seconds):
    def expired(*args):
        raise TimeoutError('Physical request wall-clock deadline')
    old = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


class Recorder:
    def __init__(self, client, out, uid):
        self.client, self.out, self.uid = client, Path(out), uid
        self.calls = self.chars = self.query_chars = self.query_calls = 0
        self.started = time.monotonic()

    def send(self, system, user, phase):
        system, user = system.strip(), user.strip()
        size = len(system) + len(user)
        remaining = BUDGET['seconds'] - (time.monotonic() - self.started)
        if remaining <= 0 or self.calls >= BUDGET['max_calls']:
            raise BudgetStop('time_or_call_budget')
        if self.chars + size > BUDGET['total_chars']:
            raise BudgetStop('total_character_budget')
        if phase == 'query' and (self.query_calls >= BUDGET['query_calls'] or self.query_chars + size > BUDGET['query_chars']):
            raise BudgetStop('query_budget_enter_final')
        if phase == 'final' and size > BUDGET['final_reserved_chars']:
            raise BudgetStop('final_context_exceeds_reservation')
        self.calls += 1
        self.chars += size
        if phase == 'query':
            self.query_calls += 1
            self.query_chars += size
        record = dict(uid=self.uid, call=self.calls, phase=phase, system=system, user=user,
                      input_chars=size, timeout_seconds=min(60,remaining), telemetry=None)
        path = self.out / 'requests' / self.uid / f'call_{self.calls:03d}.json'
        write(path, record)
        started = time.monotonic()
        telemetry_before = len(self.client.telemetry)
        original_urlopen = urllib.request.urlopen
        def transport(request, *args, **kwargs):
            payload = strict_json(request.data.decode('utf-8'))
            if payload.get('system') != system or payload.get('messages') != [{'role':'user','content':user}]:
                raise ValueError('Serialized provider request differs from recorded content')
            if 'wire_payload' in record:
                raise ValueError('Unexpected additional physical request prohibited')
            record['wire_payload'] = payload
            write(path,record)
            try:
                return original_urlopen(request,*args,**kwargs)
            except urllib.error.HTTPError as exc:
                record['http_status'] = exc.code
                raise
        try:
            with deadline(record['timeout_seconds']), patch.object(urllib.request,'urlopen',transport):
                record['response'] = self.client.complete(system,user)
        except Exception as exc:
            record['error_type'] = type(exc).__name__
            raise
        finally:
            record['elapsed_seconds'] = time.monotonic() - started
            record['telemetry'] = self.client.telemetry[-1] if len(self.client.telemetry)>telemetry_before else None
            backend = getattr(self.client,'client',None)
            if 'response' in record and hasattr(backend,'last_response'):
                record['provider_response'] = backend.last_response
            write(path, record)
        return record['response']


def valid_plan(plan):
    import jsonschema
    return isinstance(plan,dict) and jsonschema.Draft7Validator(read(SCHEMA)).is_valid(plan)


def collect_case(public, client, out):
    if set(public) != {'uid','nature_language'} or not isinstance(public['nature_language'],str) or not public['nature_language']:
        raise ValueError('Collector accepts only uid and complete original query')
    recorder, sandbox = Recorder(client,out,public['uid']), Sandbox()
    facts, plan, status, streak, query_stop = [], {}, 'not_started', 0, None
    try:
        for _ in range(BUDGET['query_calls']):
            try:
                raw = recorder.send(*context(public,facts,'query'), 'query')
            except BudgetStop as exc:
                query_stop = str(exc)
                if query_stop != 'query_budget_enter_final':
                    raise
                break
            trace = action_trace(raw,sandbox)
            trace.update(uid=public['uid'], call=recorder.calls)
            facts.append(trace)
            with (Path(out)/'tool_trace.jsonl').open('a') as stream:
                stream.write(dumps(trace)+'\n')
            obs = trace['observation']['status']
            streak = streak+1 if obs == 'protocol_error' else 0
            if streak >= 2:
                raise BudgetStop('two_consecutive_protocol_errors')
            if obs == 'finish':
                query_stop = 'model_finish'
                break
        raw = recorder.send(*context(public,facts,'final'), 'final')
        try:
            candidate = strict_json(raw)
            plan = candidate if isinstance(candidate,dict) else {}
            status = 'schema_valid' if valid_plan(plan) else 'final_schema_invalid'
        except ValueError:
            status = 'final_invalid_json'
    except BudgetStop as exc:
        status = str(exc)
    except Exception as exc:
        status = 'collection_error:' + type(exc).__name__
    result = dict(status=status, calls=recorder.calls, query_calls=recorder.query_calls,
                  chars=recorder.chars, query_chars=recorder.query_chars, query_stop=query_stop,
                  elapsed_seconds=time.monotonic()-recorder.started, schema_valid=valid_plan(plan))
    return plan, result


def source_hashes():
    files = {Path(__file__), Path(v1.__file__), CORE/'src/llm_client.py', DATA, CONFIG,
             UPSTREAM/'eval_exp.py', UPSTREAM/'data_manifest.json', UPSTREAM/'dev_hold_split.json',
             UPSTREAM/'temp_sandbox/release_manifest.json',
             CORE/'tests/test_chinatravel_pipeline.py', CORE/'tests/test_chinatravel_pipeline_v2.py'}
    files.update((UPSTREAM/'chinatravel').rglob('*.py'))
    files.update((UPSTREAM/'chinatravel/evaluation').rglob('*.json'))
    files.update((UPSTREAM/'temp_sandbox/manifests').glob('*'))
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(files) if p.is_file()}


def prepare(out):
    from llm_client import resolve_config
    raw = read(DATA)
    partitions = read(UPSTREAM/'dev_hold_split.json')['splits']
    dev = {uid for partition in partitions.values() for uid in partition['dev_uids']}
    hold = {uid for partition in partitions.values() for uid in partition['hold_uids']}
    if set(raw) != dev or dev & hold or len(dev)!=60 or len(hold)!=544:
        raise ValueError('Frozen dev/hold membership mismatch')
    ids = [REGRESSION] + [min(uid for uid,q in raw.items() if q['tag']==tag) for tag in ('medium','human')]
    public = [v1.model_input(raw[uid]) for uid in ids]
    config = resolve_config(CONFIG)
    if (config.provider,config.model,config.retries,config.max_output_tokens,config.timeout,config.max_concurrency) != (
            'xcode','claude-haiku-4-5-20251001',0,4096,60,1):
        raise ValueError('Frozen configuration does not match handoff')
    verified = v1.preflight()
    commit = subprocess.check_output(['git','-C',str(UPSTREAM),'rev-parse','HEAD'],text=True).strip()
    if commit != '0936f2727dd102ad811ed015b7bf6f7d6533f28e':
        raise ValueError('Upstream commit changed')
    out.mkdir(parents=True,exist_ok=False)
    write(out/'public_inputs.json',public)
    plan = dict(adapter='chinatravel_act_json_v2', scope='development only; first case exposed regression',
                ids=ids, selection='regression then lexicographic minimum medium and human in frozen dev',
                budget=BUDGET, policy=POLICY, system=SYSTEM, final_system=FINAL_SYSTEM, catalog=CATALOG,
                config=asdict(config), source_hashes=source_hashes(), sandbox_verified=verified,
                upstream_commit=commit,
                gate='first case schema-valid final plus completed official scoring; otherwise stop',
                public_inputs_sha256=sha(out/'public_inputs.json'))
    write(out/'plan.json',plan)
    write(out/'manifest.json',dict(adapter=plan['adapter'], ids=ids, plan_sha256=sha(out/'plan.json')))
    write(out/'predictions.json',{uid:{} for uid in ids})
    write(out/'collection.json',{'cases':{uid:{'status':'not_executed','calls':0} for uid in ids}})
    (out/'tool_trace.jsonl').touch()


def verify_sources(out):
    plan = read(out/'plan.json')
    if sha(out/'plan.json') != read(out/'manifest.json')['plan_sha256']:
        raise ValueError('Plan integrity failure')
    if source_hashes() != plan['source_hashes']:
        raise ValueError('Pinned source/data/config integrity failure')
    if sha(out/'public_inputs.json') != plan['public_inputs_sha256']:
        raise ValueError('Public inputs integrity failure')
    if plan['ids'] != read(out/'manifest.json')['ids'] or [q['uid'] for q in read(out/'public_inputs.json')] != plan['ids']:
        raise ValueError('Plan/public ID mismatch')
    v1.preflight()
    return plan


def collect_command(out, uid):
    from llm_client import LLM
    frozen = verify_sources(out)  # Hashes bytes only: no gold parsing in this collector process.
    collection = read(out/'collection.json')
    if (out/'manifest_hashes.json').exists():
        raise ValueError('Sealed archive cannot be collected again')
    if uid not in collection['cases'] or collection['cases'][uid]['status'] != 'not_executed' or (out/'requests'/uid).exists():
        raise ValueError('Unknown or already attempted case; overwrite prohibited')
    position = frozen['ids'].index(uid)
    if any(collection['cases'][prior]['status']=='not_executed' for prior in frozen['ids'][:position]):
        raise ValueError('Frozen case order must be followed')
    if position and (not collection['cases'][frozen['ids'][0]].get('schema_valid') or not (out/'official_score.json').exists()):
        raise ValueError('First case did not satisfy expansion gate')
    public = next(q for q in read(out/'public_inputs.json') if q['uid']==uid)
    prediction, result = collect_case(public, LLM(config=CONFIG),out)
    predictions = read(out/'predictions.json')
    predictions[uid] = prediction
    collection['cases'][uid] = result
    write(out/'predictions.json',predictions)
    write(out/'collection.json',collection)
    print(dumps({'uid':uid, **result}))


def score_command(out):
    if (out/'manifest_hashes.json').exists():
        raise ValueError('Use replay for a sealed archive')
    plan = verify_sources(out)
    queries = read(DATA)
    predictions = read(out/'predictions.json')
    if set(predictions) != set(plan['ids']):
        raise ValueError('Missing/extra prediction IDs')
    with offline(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        score = v1.evaluate({uid:queries[uid] for uid in plan['ids']}, predictions)
        score['per_case'] = {uid:v1.evaluate({uid:queries[uid]},{uid:predictions[uid]}) for uid in plan['ids']}
    write(out/'official_score.json',json_safe(score))


def json_safe(value):
    # Official per-constraint DataFrames pad unequal DSL lengths with NaN.
    if isinstance(value,float) and not math.isfinite(value):
        return None
    if isinstance(value,dict):
        return {key:json_safe(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):
        return [json_safe(item) for item in value]
    return value


def required_roles(out):
    cases = read(out/'collection.json')['cases']
    ids = read(out/'plan.json')['ids']
    if set(cases) != set(ids) or set(read(out/'predictions.json')) != set(ids):
        raise ValueError('Missing/extra case IDs')
    roles = {'plan.json','manifest.json','public_inputs.json','collection.json','predictions.json','tool_trace.jsonl','official_score.json'}
    for uid in ids:
        roles.update(f'requests/{uid}/call_{i:03d}.json' for i in range(1,cases[uid]['calls']+1))
    return roles


def audit_records(out):
    plan = read(out/'plan.json')
    cases = read(out/'collection.json')['cases']
    public = {q['uid']:q for q in read(out/'public_inputs.json')}
    traces = [strict_json(line) for line in (out/'tool_trace.jsonl').read_text().splitlines()]
    known = set(plan['ids'])
    if any(t['uid'] not in known for t in traces):
        raise ValueError('Unknown trace ID')
    counts, provider_in, provider_out, unknown, failures = 0, 0, 0, 0, 0
    for uid in plan['ids']:
        case = cases[uid]
        records = [read(out/f'requests/{uid}/call_{i:03d}.json') for i in range(1,case['calls']+1)]
        query_chars = total_chars = query_calls = 0
        local_traces = [t for t in traces if t['uid']==uid]
        expected_traces = [r for r in records if r['phase']=='query' and 'response' in r]
        if [t['call'] for t in local_traces] != [r['call'] for r in expected_traces]:
            raise ValueError('Trace/request count mismatch')
        for i,r in enumerate(records,1):
            if r['call'] != i or r['uid'] != uid or r['phase'] not in ('query','final'):
                raise ValueError('Request identity failure')
            prior_facts = [t for t in local_traces if t['call'] < i]
            system,user = context(public[uid],prior_facts,r['phase'])
            if (r['system'],r['user']) != (system,user):
                raise ValueError('Request context mismatch')
            chars = len(system)+len(user)
            if r['input_chars'] != chars or not 0 < r['timeout_seconds'] <= 60:
                raise ValueError('Request accounting failure')
            if 'wire_payload' in r:
                payload = r['wire_payload']
                if payload.get('system') != system or payload.get('messages') != [{'role':'user','content':user}]:
                    raise ValueError('Wire payload content mismatch')
                if payload.get('model') != plan['config']['model'] or payload.get('max_tokens') != 4096:
                    raise ValueError('Wire model/output budget mismatch')
            total_chars += chars
            if r['phase']=='query':
                query_calls += 1
                query_chars += chars
            elif i != len(records) or chars > 50000:
                raise ValueError('Final request reservation/order failure')
            telemetry = r['telemetry']
            if telemetry and telemetry['attempts'] != 1:
                raise ValueError('Unbudgeted retries detected')
            if telemetry and telemetry['usage_source']=='provider':
                provider_in += telemetry['input_tokens']; provider_out += telemetry['output_tokens']
            else:
                unknown += 1
            failures += int('error_type' in r)
        for trace,r in zip(local_traces,expected_traces):
            if trace['raw_response'] != r['response']:
                raise ValueError('Trace raw response mismatch')
        if len(records)>12 or query_calls>8 or total_chars>160000 or query_chars>110000:
            raise ValueError('Budget exceeded')
        if records and (case['chars'],case['query_chars'],case['query_calls']) != (total_chars,query_chars,query_calls):
            raise ValueError('Collection accounting mismatch')
        if not records and case['status'] != 'not_executed':
            raise ValueError('Missing attempted-case requests')
        final = [r for r in records if r['phase']=='final' and 'response' in r]
        derived = {}
        if final:
            try:
                candidate = strict_json(final[0]['response'])
                derived = candidate if isinstance(candidate,dict) else {}
            except ValueError:
                pass
        if read(out/'predictions.json')[uid] != derived:
            raise ValueError('Prediction does not match raw final output')
        counts += len(records)
    if counts > 36:
        raise ValueError('Round request limit exceeded')
    return dict(physical_requests=counts, transport_failures=failures, usage_unknown=unknown,
                provider_input_tokens=provider_in, provider_output_tokens=provider_out)


def seal(out):
    roles = required_roles(out)
    write(out/'manifest_hashes.json',{role:sha(out/role) for role in sorted(roles)})


def replay(out):
    with offline():
        verify_sources(out)
        roles = required_roles(out)
        hashes = read(out/'manifest_hashes.json')
        if set(hashes) != roles:
            raise ValueError('Required file roles missing or unexpected')
        actual = {str(p.relative_to(out)) for p in (out/'requests').rglob('*.json')} if (out/'requests').exists() else set()
        if actual != {r for r in roles if r.startswith('requests/')}:
            raise ValueError('Request file count mismatch')
        for role in roles:
            if sha(out/role) != hashes[role]:
                raise ValueError('Artifact integrity failure: '+role)
        audit = audit_records(out)
        previous = read(out/'official_score.json')
        # Scoring occurs only in a distinct process/command after collection.
        queries = read(DATA)
        predictions = read(out/'predictions.json')
        ids = read(out/'plan.json')['ids']
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            score = v1.evaluate({uid:queries[uid] for uid in ids},predictions)
            score['per_case'] = {uid:v1.evaluate({uid:queries[uid]},{uid:predictions[uid]}) for uid in ids}
        if json_safe(score) != previous:
            raise ValueError('Offline score mismatch')
        result = dict(status='PASS', network='socket connections blocked', score_identical=True, **audit)
        write(out/'replay_report.json',result)
        return result


def run(out):
    prepare(out)
    ids = read(out/'plan.json')['ids']
    for index,uid in enumerate(ids):
        subprocess.run([sys.executable,__file__,'collect','--run-dir',str(out),'--uid',uid],check=True)
        subprocess.run([sys.executable,__file__,'score','--run-dir',str(out)],check=True)
        case = read(out/'collection.json')['cases'][uid]
        if index==0 and not case.get('schema_valid'):
            break
    seal(out)
    print(dumps(replay(out)))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('command',choices=['run','prepare','collect','score','replay'])
    parser.add_argument('--run-dir',required=True)
    parser.add_argument('--uid')
    args = parser.parse_args()
    out = Path(args.run_dir).resolve()
    if args.command=='collect':
        collect_command(out,args.uid)
    elif args.command=='score':
        score_command(out)
    elif args.command=='replay':
        print(dumps(replay(out)))
    elif args.command=='prepare':
        prepare(out)
    else:
        run(out)


if __name__=='__main__':
    main()
