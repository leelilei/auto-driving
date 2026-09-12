import pytest
from scripts import run_fair30_interface as runner


@pytest.fixture
def mock_run(tmp_path):
    run=tmp_path/'run'
    runner.prepare(run,mode='MOCK')
    with runner.base.NetworkBlocker():
        runner.collect(run)
    return run


def test_complete_replay_and_denominators(mock_run):
    result=runner.audit(mock_run)
    assert result['logical_units']==result['physical_calls']==result['independent_decisions']==120
    assert all(x['n']==30 for x in result['arms'].values())
    assert result['scope']=='MOCK_ENGINEERING_ONLY'


def test_missing_record_rejected(mock_run):
    next((mock_run/'attempts').glob('*.json')).unlink()
    with pytest.raises(ValueError,match='Missing'):
        runner.audit(mock_run)


def test_request_tampering_rejected(mock_run):
    path=next((mock_run/'attempts').glob('*.json'))
    record=runner.base.read(path)
    record['request']['user']='{}'
    runner.base.write(path,record)
    with pytest.raises(ValueError,match='Changed request'):
        runner.audit(mock_run)


def test_success_resampling_rejected(mock_run):
    path=next((mock_run/'attempts').glob('*.json'))
    runner.base.write(path.with_name(path.name.replace('.a1.','.a2.')),runner.base.read(path))
    with pytest.raises(ValueError,match='Illegal semantic'):
        runner.audit(mock_run)


def test_schema_failure_retained_with_fallback(tmp_path,monkeypatch):
    run=tmp_path/'run'
    runner.prepare(run,mode='MOCK')
    old=runner.mock_response
    monkeypatch.setattr(runner,'mock_response',lambda j,refs:'{}' if j['call_id']=='F01__original__language' else old(j,refs))
    with runner.base.NetworkBlocker():runner.collect(run)
    result=runner.audit(run)
    assert result['arms']['original_language']['schema_failed']==1
    assert len(runner.records(run,'F01__original__language'))==1
    row=next(x for x in result['rows'] if x['call_id']=='F01__original__language')
    assert row['object_success'] and not row['raw_task_success']
