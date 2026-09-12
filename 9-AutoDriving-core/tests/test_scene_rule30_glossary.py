import json
import shutil
import pytest
from scripts import scene_rule30_glossary as g

@pytest.fixture(scope='module')
def baseline(tmp_path_factory):
    run=tmp_path_factory.mktemp('glossary')/'mock';g.prepare(run,mode='MOCK')
    with g.base.NetworkBlocker():g.collect(run)
    return run

@pytest.fixture
def run(baseline,tmp_path):
    dest=tmp_path/'run';shutil.copytree(baseline,dest);return dest

def test_same_candidates_and_only_fixed_glossary_added(run):
    refs=g.base.read(run/'reference_records.json')
    for j in g.base.read(run/'plan.json'):
        old=refs[f"{j['case_id']}__r{j['rep']}__language"]['request']
        assert j['request']['user']==old['user']
        assert j['request']['system']==old['system']+g.GLOSSARY
        assert json.loads(j['request']['user'])['computed_scene_facts'] is None
    with g.base.NetworkBlocker():out=g.replay(run)
    assert out==g.base.read(run/'summary.json')
    assert out['scope']=='MOCK_ENGINEERING_ONLY'
    assert out['physical_calls']==out['logical_units']==60
    assert out['by_stratum']['primary']['n']==36
    assert out['by_stratum']['control']['n']==24

@pytest.mark.parametrize('mutation',['delete','parsed','request','provenance','skip_attempt'])
def test_incomplete_or_tampered_run_rejected(run,mutation):
    path=run/'attempts/R01__r1__glossary.a1.json';r=g.base.read(path)
    if mutation=='delete':path.unlink()
    elif mutation=='skip_attempt':path.rename(path.with_name('R01__r1__glossary.a2.json'))
    else:
        if mutation=='parsed':r['parsed_policy']['return_by']=550
        elif mutation=='request':r['request']['system']='changed'
        elif mutation=='provenance':r['source']='REAL'
        g.base.write(path,r)
    with g.base.NetworkBlocker(),pytest.raises(ValueError):g.replay(run)

def test_failed_review_falls_back_without_denominator_change(run):
    path=run/'attempts/R01__r1__glossary.a1.json';r=g.base.read(path)
    r.update(status='SCHEMA_FAILED',raw_response='not json');g.base.write(path,r)
    with g.base.NetworkBlocker():out=g.replay(run)
    assert out['glossary']['n']==60 and out['glossary']['fallback']==1
    row=next(x for x in out['rows'] if x['call_id']=='R01__r1__glossary')
    source=g.base.read(run/'reference_records.json')['R01__r1__direct']['parsed_policy']
    assert row['policy']==source
