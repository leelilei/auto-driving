"""Small scene-conditional DSL. Facts accept a scene only; execution accepts predictions."""
from dataclasses import asdict, dataclass
import json
import math
import re

SELECTIONS={'nearest_from_bank','minimum_added_distance','highest_rating'}

def number(value, label, minimum=None, maximum=None):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(f'{label}: finite number required')
    if minimum is not None and value<minimum or maximum is not None and value>maximum:
        raise ValueError(f'{label}: outside supported range')
    return value

@dataclass(frozen=True)
class Policy:
    selection: str
    availability_reference: str
    return_by: int | None

    @classmethod
    def parse(cls, value):
        if not isinstance(value,dict) or set(value)!={'selection','availability_reference','return_by'}:
            raise ValueError('policy must contain exactly three declared fields')
        if not isinstance(value['selection'],str) or value['selection'] not in SELECTIONS or value['availability_reference'] not in ('arrival','departure'):
            raise ValueError('unknown selection or availability reference')
        t=value['return_by']
        if t is not None:
            if isinstance(t,bool) or not isinstance(t,int) or not 0<=t<=1440:
                raise ValueError('return_by must be integer minutes or null')
        return cls(**value)

    def to_dict(self): return asdict(self)

def decode_response_object(raw):
    # A single complete Markdown JSON wrapper is serialization, not a rule edit.
    match=re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*',raw,re.DOTALL)
    if match:raw=match.group(1)
    return json.loads(raw)

def parse_response(raw):
    value=decode_response_object(raw)
    if not isinstance(value,dict) or set(value)!={'selection','availability_reference','return_by','evidence'}:
        raise ValueError('response must contain three policy fields and evidence')
    if not isinstance(value['evidence'],dict):raise ValueError('evidence must be an object')
    return Policy.parse({k:v for k,v in value.items() if k!='evidence'}), value['evidence']

def validate_scene(scene):
    required={'home','departure','speed_units_per_minute','bank','bank_service','pharmacy_service','pharmacies'}
    if not isinstance(scene,dict) or set(scene)!=required:raise ValueError('invalid scene fields')
    if not isinstance(scene['home'],list) or len(scene['home'])!=2:raise ValueError('invalid home coordinate')
    for x in scene['home']:number(x,'home coordinate')
    number(scene['departure'],'departure',0,1440)
    number(scene['bank_service'],'bank service',0)
    number(scene['pharmacy_service'],'pharmacy service',0)
    if number(scene['speed_units_per_minute'],'speed')<=0:raise ValueError('speed must be positive')
    if not isinstance(scene['pharmacies'],dict) or not scene['pharmacies']:raise ValueError('empty pharmacies')
    if not all(isinstance(k,str) and k for k in scene['pharmacies']):raise ValueError('invalid pharmacy id')
    for node in [scene['bank'],*scene['pharmacies'].values()]:
        if not isinstance(node,dict) or set(node)!={'x','y','open','close','rating'}:raise ValueError('invalid node fields')
        for k in ('x','y'):number(node[k],k)
        number(node['open'],'open',0,1440);number(node['close'],'close',0,1440)
        number(node['rating'],'rating',0,5)
        if node['close']<node['open']:raise ValueError('overnight windows not supported')

def scene_facts(scene):
    """All public candidate facts; no policy, instruction, cutoff, gold or ranking input."""
    validate_scene(scene)
    bank=scene['bank'];home=scene['home'];bp=(bank['x'],bank['y'])
    speed=scene['speed_units_per_minute']
    leg=lambda a,b:math.hypot(a[0]-b[0],a[1]-b[1])
    bank_arrival=scene['departure']+leg(home,bp)/speed
    bank_finish=bank_arrival+scene['bank_service']
    bank_valid=bank['open']<=bank_arrival and bank_finish<=bank['close']
    rows=[]
    for pid in sorted(scene['pharmacies']):
        p=scene['pharmacies'][pid];pp=(p['x'],p['y']);out=leg(bp,pp);back=leg(pp,home)
        arrival=bank_finish+out/speed;finish=arrival+scene['pharmacy_service']
        rows.append(dict(poi_id=pid,distance_from_bank=out,added_distance=out+back-leg(bp,home),
                         arrival=arrival,service_finish=finish,return_time=finish+back/speed,rating=p['rating'],
                         open_at_departure=p['open']<=scene['departure']<p['close'],
                         service_window_ok=p['open']<=arrival and finish<=p['close']))
    return dict(bank_arrival=bank_arrival,bank_service_finish=bank_finish,bank_service_window_ok=bank_valid,
                candidates=rows,notes='No waiting. Candidate facts do not identify the user selection rule.')

def execute(scene, policy):
    if not isinstance(policy,Policy):raise TypeError('execute requires a validated predicted Policy')
    facts=scene_facts(scene);eligible=[]
    for r in facts['candidates']:
        if not facts['bank_service_window_ok'] or not r['service_window_ok']:continue
        if policy.availability_reference=='departure' and not r['open_at_departure']:continue
        if policy.return_by is not None and r['return_time']>policy.return_by:continue
        value={'nearest_from_bank':r['distance_from_bank'],'minimum_added_distance':r['added_distance'],'highest_rating':-r['rating']}[policy.selection]
        eligible.append((r['poi_id'],value))
    if not eligible:return {'status':'INFEASIBLE','selected_poi_ids':[]}
    best=min(v for _,v in eligible)
    accepted=sorted(pid for pid,v in eligible if math.isclose(v,best,rel_tol=0,abs_tol=1e-9))
    return {'status':'OK','selected_poi_ids':accepted}

def evaluate(policy, decision, gold):
    """Independent saved author reference, never passed into the method executor."""
    rule_correct=policy is not None and policy.to_dict()==gold['policy']
    if decision is None:return dict(rule_correct=False,object_success=False,feasible_success=False,false_infeasible=False)
    ids=decision['selected_poi_ids'];status=decision['status']
    if status=='INFEASIBLE':
        success=gold['status']=='INFEASIBLE' and not ids
        feasible=success
    else:
        success=status=='OK' and bool(ids) and set(ids)<=set(gold['accepted_poi_ids'])
        feasible_ids={r['poi_id'] for r in gold['candidates'] if r['feasible']}
        feasible=status=='OK' and bool(ids) and set(ids)<=feasible_ids
    return dict(rule_correct=rule_correct,object_success=success,feasible_success=feasible,
                false_infeasible=status=='INFEASIBLE' and gold['status']!='INFEASIBLE')

DIRECT_SYSTEM='''Extract the selection rule expressed by the instruction, using the full public scene when needed. Return only a JSON object with exactly selection, availability_reference, return_by, evidence.
selection is nearest_from_bank, minimum_added_distance, or highest_rating.
availability_reference is departure only when already open at home departure is explicitly required, otherwise arrival.
return_by is integer minutes since midnight or null when absent. It is the requested deadline, not a computed arrival time.
evidence is an object quoting instruction spans. Keep the instruction's requirements even if they are infeasible. Do not choose a pharmacy ID or relax a rule. The shared executor handles travel, service windows, no waiting and final selection.'''
REVIEW_SYSTEM='''Review the predicted selection rule against the instruction and full public scene. The prediction may be wrong. Supplementary computed facts are consequences only and cannot override what the instruction requests. Check every field, including when the prediction seems feasible. Return only a JSON object with exactly selection, availability_reference, return_by, evidence.
selection is nearest_from_bank, minimum_added_distance, or highest_rating.
availability_reference is departure only when already open at home departure is explicitly required, otherwise arrival.
return_by is integer minutes since midnight or null when absent. It is the requested deadline, not a computed arrival time.
evidence quotes instruction spans. Preserve the requirements even if infeasible. Do not choose a pharmacy ID or relax a rule.'''

def request(public, role, candidate=None):
    if role not in ('direct','language','evidence'):raise ValueError('unknown role')
    # Whitelist fields; bookkeeping IDs and any injected private metadata are ignored.
    value={'instruction':public['instruction'],'scene':public['scene']}
    if role!='direct':
        if not isinstance(candidate,Policy):raise ValueError('valid direct candidate required')
        value['candidate_policy']=candidate.to_dict()
        value['computed_scene_facts']=scene_facts(public['scene']) if role=='evidence' else None
    return {'system':DIRECT_SYSTEM if role=='direct' else REVIEW_SYSTEM,
            'user':json.dumps(value,ensure_ascii=False,sort_keys=True)}
