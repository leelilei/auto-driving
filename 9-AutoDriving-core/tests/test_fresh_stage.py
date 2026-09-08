from dataclasses import replace
from pathlib import Path
import json
import pytest
from scripts import run_fresh_stage as f
from src.llm_client import LLMConfig

def record():
    return dict(group_id='test_001',utterance_id='test_001_v0',variant_type='V0',text='Visit the bank.',source_index=1,preference_direction='balanced',gold_hard=dict(pois=['bank'],time_limit=None,dependencies=[]))

def test_variants_and_unique_ids_required():
    r=record()
    with pytest.raises(ValueError):f.validate([r]*4,4)
    rs=[dict(r,utterance_id=f'u{i}',variant_type=f'V{i}') for i in range(4)]
    assert len(f.validate(rs,4))==1

def test_collects_five_independent_draws_and_preserves_raw(monkeypatch,tmp_path):
    class Fake:
        def __init__(self,cfg):self.telemetry=[]
        def complete(self,system,user):
            self.telemetry.append(dict(usage_source='provider',total_tokens=12))
            return json.dumps(dict(pois=['bank'],time_limit=None,dependencies=[],quality_weight=.5))
    monkeypatch.setattr(f,'LLM',Fake);(tmp_path/'attempts').mkdir()
    us,g=f.run_group([record()],LLMConfig(),tmp_path,'main')
    assert set(us[0]['calls'])=={'A','B','review','A2','A3'}
    assert len(list((tmp_path/'attempts').glob('*_finished.json')))==5
    metrics,rs=f.evaluate(us,{'test_001':g},dict(tau_star=.02,tau_sem_star=.1,p_review_star=.48),'main')
    assert len(metrics)==8 and metrics['B0']['TSR']==1
    assert metrics['B1']['known_provider_tokens']==36
    assert metrics['B0']['regret']==0
    with pytest.raises(FileExistsError):f.write(tmp_path/'test_001.json',{})

def test_transport_failure_preserved_and_stops_group(monkeypatch,tmp_path):
    class Fail:
        def __init__(self,cfg):self.telemetry=[]
        def complete(self,*args):raise RuntimeError('connection failure')
    monkeypatch.setattr(f,'LLM',Fail);(tmp_path/'attempts').mkdir()
    us,g=f.run_group([record(),dict(record(),utterance_id='other')],LLMConfig(),tmp_path,'pilot')
    assert len(us)==1 and len(us[0]['calls'])==1
    assert us[0]['calls']['A']['transport_error_type']=='RuntimeError'
    assert (tmp_path/'attempts/test_001_v0_A_finished.json').exists()

def test_partial_failure_evaluation_handles_unattempted_calls(monkeypatch,tmp_path):
    class Fail:
        def __init__(self,cfg):self.telemetry=[]
        def complete(self,*args):raise RuntimeError('provider HTTP 502')
    monkeypatch.setattr(f,'LLM',Fail);(tmp_path/'attempts').mkdir()
    us,g=f.run_group([record()],LLMConfig(),tmp_path,'pilot')
    metrics,rs=f.evaluate(us,{'test_001':g},dict(tau_star=.02,tau_sem_star=.1,p_review_star=.48),'pilot')
    assert metrics['Ours']['usage_complete'] is False
    assert metrics['Ours']['regret'] is None
    assert metrics['Ours']['TSR']==0

def test_main_rejects_missing_admission_before_creating_run(monkeypatch,tmp_path):
    data=[]
    for g in range(160):
        for v in range(4):data.append(dict(record(),group_id=f'test_{g:03}',utterance_id=f'test_{g:03}_v{v}',variant_type=f'V{v}'))
    dataset=tmp_path/'dataset.json';dataset.write_text(json.dumps(data))
    monkeypatch.setattr('sys.argv',['run_fresh_stage.py','--stage','main','--dataset',str(dataset)])
    with pytest.raises(ValueError,match='admission'):f.main()
