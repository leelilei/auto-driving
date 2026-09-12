import json
import pytest
from scripts import prepare_scene_fair30 as data
from scripts import scene_fair30 as runner
from scripts.scene_rule30_glossary import GLOSSARY
from src.scene_policy import Policy


def test_sample_is_deterministic_complete_and_arithmetic_checked(tmp_path):
    out = tmp_path/'data'
    report = data.prepare(out)
    assert len(data.build_cases()) == 30
    assert data.build_cases() == json.loads((out/'author_review_cases.json').read_text())
    assert report['feasible'] + report['infeasible'] == 30
    assert set(report['selections'].values()) == {10}
    assert len(json.loads((out/'run_plan.json').read_text())) == 180
    with pytest.raises(ValueError, match='Refuse overwrite'):
        data.prepare(out)


def test_equal_definitions_and_scene_only_evidence():
    case = data.build_cases()[0]
    candidate = Policy('highest_rating', 'arrival', None)
    requests = {r:runner.request(case, r, candidate if r!='direct' else None) for r in runner.base.ROLES}
    assert all(p['system'].endswith(GLOSSARY) and p['system'].count(GLOSSARY)==1 for p in requests.values())
    language = json.loads(requests['language']['user'])
    evidence = json.loads(requests['evidence']['user'])
    assert requests['language']['system'] == requests['evidence']['system']
    assert language.pop('computed_scene_facts') is None
    assert evidence.pop('computed_scene_facts')['candidates']
    assert language == evidence
    assert set(json.loads(requests['direct']['user'])) == {'instruction', 'scene'}
    assert 'author_policy' not in requests['direct']['user']


def test_real_collection_refuses_missing_review_before_client(tmp_path, monkeypatch):
    run = tmp_path/'real'
    runner.prepare(run)
    monkeypatch.setattr(runner.base, 'collect', lambda *a, **k:pytest.fail('collector must not run'))
    with pytest.raises(ValueError, match='PENDING'):
        runner.collect(run)
    assert not list((run/'attempts').glob('*'))


def test_mock_replay_and_missing_record_rejection(tmp_path):
    run = tmp_path/'mock'
    runner.prepare(run, mode='MOCK')
    with runner.base.NetworkBlocker():
        runner.collect(run)
    summary = runner.audit(run)
    assert summary['logical_units'] == 180
    assert summary['independent_decisions_verified'] == 180
    assert summary['scope'] == 'MOCK_ENGINEERING_ONLY'
    assert all(v['n']==60 for v in summary['methods'].values())
    next((run/'attempts').glob('*.json')).unlink()
    with pytest.raises(ValueError, match='missing'):
        runner.audit(run)


def test_wrong_dataset_review_is_rejected(tmp_path):
    receipt = tmp_path/'review.json'
    runner.base.write(receipt, dict(status='APPROVED', reviewer='test fixture', reviewed_at='test', approval_evidence='synthetic test only',
        dataset_manifest_sha256='wrong', approved_case_ids=[c['case_id'] for c in data.build_cases()]))
    run = tmp_path/'run'
    runner.prepare(run, receipt=receipt)
    with pytest.raises(ValueError, match='exact dataset'):
        runner.require_review(run)
