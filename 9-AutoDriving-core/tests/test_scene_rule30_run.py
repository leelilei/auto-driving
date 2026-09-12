import shutil
import pytest
from scripts import scene_rule30_run as r

@pytest.fixture(scope='module')
def baseline(tmp_path_factory):
    run=tmp_path_factory.mktemp('rule30')/'mock'
    r.prepare(run,16,mode='MOCK')
    with r.NetworkBlocker():r.collect(run)
    return run

@pytest.fixture
def run(baseline,tmp_path):
    path=tmp_path/'copy';shutil.copytree(baseline,path);return path

def test_full_180_reconstruction_and_denominators(run):
    with r.NetworkBlocker():out=r.replay(run)
    assert out==r.read(run/'summary.json')
    assert out['scope']=='MOCK_ENGINEERING_ONLY'
    assert out['logical_units']==out['physical_calls']==180
    assert out['independent_decisions_verified']==180
    for role in r.ROLES:
        assert out['methods'][role]['n']==60
        assert out['by_stratum']['primary'][role]['n']==36
        assert out['by_stratum']['control'][role]['n']==24
    assert len(out['by_block'])==12

@pytest.mark.parametrize('bad',['missing','extra','changed_request','parsed','raw','provenance','snapshot','illegal_retry'])
def test_replay_rejects_damaged_run(run,bad):
    path=run/'attempts/R01__r1__direct.a1.json';record=r.read(path)
    if bad=='missing':path.unlink()
    elif bad=='extra':r.write(run/'attempts/extra.json',record)
    elif bad=='snapshot':r.write(run/'run_plan.json',[])
    elif bad=='illegal_retry':r.write(path.with_name('R01__r1__direct.a2.json'),record)
    else:
        if bad=='changed_request':record['request']['user']='different'
        elif bad=='parsed':record['parsed_policy']['return_by']=550
        elif bad=='raw':record['raw_response']='not JSON'
        elif bad=='provenance':record['source']='REAL'
        r.write(path,record)
    with r.NetworkBlocker(),pytest.raises((ValueError,KeyError)):
        r.replay(run)

def test_failures_keep_fixed_denominators(run):
    p=run/'attempts/R01__r1__language.a1.json';a=r.read(p)
    a.update(status='SCHEMA_FAILED',raw_response='bad');r.write(p,a)
    p=run/'attempts/R02__r1__direct.a1.json';a=r.read(p)
    a.update(status='SCHEMA_FAILED',raw_response='bad');r.write(p,a)
    for role in ('language','evidence'):
        cid=f'R02__r1__{role}'
        r.write(run/'attempts'/f'{cid}.a1.json',dict(call_id=cid,case_id='R02',rep=1,role=role,status='UPSTREAM_SCHEMA_FAILED',source='MOCK'))
    with r.NetworkBlocker():out=r.replay(run)
    assert out['physical_calls']==178
    assert out['methods']['language']['n']==60
    assert out['methods']['language']['fallback']==1
    assert out['status_counts']['evidence']['UPSTREAM_SCHEMA_FAILED']==1

def test_explicit_transport_recovery_preserves_scoring(run):
    expected=r.read(run/'summary.json')['methods']
    r.amend_transport(run,8)
    path=run/'attempts/R01__r1__direct.a1.json';original=r.read(path)
    failed=dict(original,status='TRANSPORT_FAILED',error='offline test reset')
    failed.pop('raw_response');failed.pop('parsed_policy')
    r.write(path,failed);r.write(path.with_name('R01__r1__direct.a2.json'),failed)
    r.write(path.with_name('R01__r1__direct.a3.json'),original)
    with r.NetworkBlocker():out=r.replay(run)
    assert out['methods']==expected and out['physical_calls']==182 and out['recoveries']==2
    assert out['concurrency']==8
    with pytest.raises(ValueError,match='already exists'):r.amend_transport(run,4)
