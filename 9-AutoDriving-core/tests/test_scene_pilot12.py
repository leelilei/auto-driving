"""Engineering checks on authored development fixtures; no model inference."""
from copy import deepcopy
import json
import pytest

from src.scene_policy import Policy, execute, evaluate, request, scene_facts, parse_response
from scripts import scene_pilot12 as runner

PUBLIC=runner.read(runner.DATA/'model_inputs.json')
GOLD=runner.read(runner.DATA/'gold_and_traces.json')

def test_json_wrapper_preserves_semantics():
    raw=json.dumps(dict(**GOLD[0]['policy'],evidence={}))
    assert parse_response(raw)==parse_response('```json\n'+raw+'\n```')
    with pytest.raises(ValueError):parse_response('Explanation\n```json\n'+raw+'\n```')
    with pytest.raises(ValueError):parse_response('```json\n'+raw+'\n```\n{}')
    bad=json.dumps(dict(**GOLD[0]['policy'],evidence={},unexpected=1))
    with pytest.raises(ValueError):parse_response('```json\n'+bad+'\n```')

@pytest.mark.parametrize('index',range(12))
def test_independent_reference(index):
    g=GOLD[index]
    decision=execute(PUBLIC[index]['scene'],Policy.parse(g['policy']))
    assert decision=={'status':g['status'],'selected_poi_ids':g['accepted_poi_ids']}
    assert evaluate(Policy.parse(g['policy']),decision,g)['object_success']

def test_boundary_speed_and_no_waiting():
    p=Policy.parse(GOLD[7]['policy']);scene=deepcopy(PUBLIC[7]['scene'])
    assert execute(scene,p)['selected_poi_ids']==['P_alpha']  # finish == close
    scene['pharmacies']['P_alpha']['close']-=0.01
    assert execute(scene,p)['selected_poi_ids']==['P_beta']
    scene['speed_units_per_minute']=2
    assert scene_facts(scene)['bank_service_finish']==565
    scene['bank']['open']=546  # arrives 545; waiting forbidden
    assert execute(scene,p)['status']=='INFEASIBLE'

def test_return_deadline_and_ties():
    scene=deepcopy(PUBLIC[3]['scene']);p=Policy('highest_rating','arrival',600)
    assert execute(scene,p)['selected_poi_ids']==['P_beta']
    assert execute(scene,Policy('highest_rating','arrival',599))['selected_poi_ids']==['P_alpha']
    scene['pharmacies']['P_beta']=deepcopy(scene['pharmacies']['P_alpha'])
    assert execute(scene,p)['selected_poi_ids']==['P_alpha','P_beta']

@pytest.mark.parametrize('field,value',[('return_by',True),('return_by',1.5),('return_by',1441),('selection',[]),('selection','hash'),('availability_reference','later')])
def test_invalid_policy(field,value):
    p=dict(GOLD[0]['policy']);p[field]=value
    with pytest.raises(ValueError):Policy.parse(p)

def test_scene_nonfinite():
    scene=deepcopy(PUBLIC[0]['scene']);scene['home'][0]=float('nan')
    with pytest.raises(ValueError):scene_facts(scene)

def test_wrong_predictions_reach_executor():
    # nearest != minimum added distance; no oracle substitution
    wrong=Policy('nearest_from_bank','arrival',None)
    d=execute(PUBLIC[4]['scene'],wrong)
    assert d['selected_poi_ids']==['P_alpha']
    assert not evaluate(wrong,d,GOLD[4])['object_success']
    # coincidence does not count as correct language parsing
    wrong=Policy('highest_rating','arrival',None)
    d=execute(PUBLIC[1]['scene'],wrong)
    assert not evaluate(wrong,d,GOLD[1])['rule_correct']
    wrong=Policy('nearest_from_bank','arrival',550)
    assert evaluate(wrong,execute(PUBLIC[0]['scene'],wrong),GOLD[0])['false_infeasible']

def test_open_reference():
    scene=PUBLIC[8]['scene']
    assert execute(scene,Policy('nearest_from_bank','departure',None))['selected_poi_ids']==['P_beta']
    assert execute(scene,Policy('nearest_from_bank','arrival',None))['selected_poi_ids']==['P_alpha']

def test_prompt_isolation_and_matched_reviews():
    public=deepcopy(PUBLIC[0]);public.update(gold='SECRET',pair_id='SECRET',human_review_status='SECRET')
    p=Policy.parse(GOLD[0]['policy'])
    direct=request(public,'direct')
    assert 'SECRET' not in direct['user'] and 'case_id' not in direct['user']
    language=request(public,'language',p);evidence=request(public,'evidence',p)
    assert language['system']==evidence['system']
    a=json.loads(language['user']);b=json.loads(evidence['user'])
    assert a.pop('computed_scene_facts') is None
    facts=b.pop('computed_scene_facts');assert a==b
    assert len(facts['candidates'])==2
    keys=set(facts)|set().union(*(set(r) for r in facts['candidates']))
    assert not keys & {'accepted_poi_ids','return_by','selection','feasible'}

@pytest.fixture
def mock_run(tmp_path):
    run=tmp_path/'mock'
    runner.prepare(run)
    with runner.NetworkBlocker():runner.collect(run,mock=True)
    return run

def test_mock_replay_and_pending_admission(mock_run):
    with runner.NetworkBlocker():
        result=runner.replay(mock_run,save=False)
        with pytest.raises(ValueError,match='not approved'):
            runner.collect(mock_run,mock_run/'admission_template.json')
    assert result['scope']=='MOCK_ENGINEERING_ONLY'
    assert result['logical_units']==result['physical_calls']==72
    assert len(result['pair_results'])==36
    assert result['by_gold_status']['INFEASIBLE']['direct']['n']==4

@pytest.mark.parametrize('mutation',['delete','request','raw','parsed','source','duplicate','snapshot','skip','empty'])
def test_replay_rejects_bad_evidence(mock_run,mutation):
    path=mock_run/'attempts/S01__r1__direct.a1.json';record=runner.read(path)
    if mutation=='delete':path.unlink()
    elif mutation=='empty':
        for p in (mock_run/'attempts').glob('*.json'):p.unlink()
    elif mutation=='snapshot':
        (mock_run/'model_inputs.json').write_text('[]')
    elif mutation=='duplicate':runner.write(path.with_name('S01__r1__direct.a2.json'),record)
    else:
        if mutation=='request':record['request']['user']='changed'
        elif mutation=='raw':record.pop('raw_response')
        elif mutation=='parsed':record['parsed_policy']['return_by']=123
        elif mutation=='source':record['source']='REAL'
        elif mutation=='skip':record['status']='UPSTREAM_SCHEMA_FAILED'
        runner.write(path,record)
    with runner.NetworkBlocker(),pytest.raises((ValueError,KeyError,FileNotFoundError)):
        runner.replay(mock_run,save=False)

def test_schema_skip_and_review_fallback(mock_run):
    # Explicit mock ledger only; simulate invalid review and invalid upstream.
    path=mock_run/'attempts/S01__r1__language.a1.json';r=runner.read(path)
    r.update(status='SCHEMA_FAILED',raw_response='not json');runner.write(path,r)
    path=mock_run/'attempts/S02__r1__direct.a1.json';r=runner.read(path)
    r.update(status='SCHEMA_FAILED',raw_response='not json');runner.write(path,r)
    for role in ('language','evidence'):
        cid=f'S02__r1__{role}'
        runner.write(mock_run/'attempts'/f'{cid}.a1.json',dict(call_id=cid,role=role,source='MOCK',status='UPSTREAM_SCHEMA_FAILED'))
    result=runner.replay(mock_run,save=False)
    rows={r['call_id']:r for r in result['rows']}
    assert rows['S01__r1__language']['fallback']
    assert not rows['S02__r1__evidence']['object_success']
    assert result['physical_calls']==70
    assert result['methods']['evidence']['n']==24

def test_development_authorization_keeps_review_pending(tmp_path,monkeypatch):
    run=tmp_path/'development'
    runner.prepare(run,development_authorization='TEST FIXTURE: authorized development only')
    monkeypatch.setenv('DEEPSEEK_API_KEY','test-placeholder')
    class OfflineClient:
        def __init__(self,config):
            self.telemetry=[];self.client=self;self.last_response=None
        def complete(self,**payload):
            self.telemetry.append({'usage_source':'mock','total_tokens':0})
            return json.dumps(dict(selection='nearest_from_bank',availability_reference='arrival',return_by=None,evidence={}))
    monkeypatch.setattr(runner,'LLM',OfflineClient)
    with runner.NetworkBlocker():runner.collect(run,development=True)
    assert runner.read(run/'summary.json')['scope']=='UNREVIEWED_DEVELOPMENT_ONLY'
    assert runner.read(run/'admission_template.json')['status']=='PENDING'
    assert not (run/'admission.json').exists()
    with pytest.raises(ValueError,match='missing'):
        runner.collect(run)

def test_development_requires_frozen_authorization(tmp_path):
    run=tmp_path/'unapproved';runner.prepare(run)
    with pytest.raises(ValueError,match='not frozen'):
        runner.collect(run,development=True)
