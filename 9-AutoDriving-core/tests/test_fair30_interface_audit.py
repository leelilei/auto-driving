import json
import pytest
from scripts import prepare_fair30_interface_audit as audit


def test_clarification_changes_only_responsibility_sentence():
    case = audit.fair.base.read(audit.REFERENCE/'model_inputs.json')[0]
    changed = audit.clarified(case)
    assert changed['scene'] == case['scene']
    assert changed['instruction'].replace(audit.NEW, audit.OLD) == case['instruction']
    assert case['instruction'].count(audit.OLD) == 1
    with pytest.raises(ValueError):
        audit.clarified(changed)


def test_plan_balanced_matched_and_no_gold_in_requests(tmp_path):
    out = tmp_path/'diagnostic'
    result = audit.prepare(out)
    plan = audit.fair.base.read(out/'request_plan.json')
    assert result['model_api_calls'] == 0 and len(plan) == 120
    assert len({j['call_id'] for j in plan}) == 120
    for cid in {j['case_id'] for j in plan}:
        arms = [j for j in plan if j['case_id']==cid]
        assert len(arms) == 4
        assert len({j['candidate_source'] for j in arms}) == 1
        assert len({j['request']['system'] for j in arms}) == 1
        payloads = {(j['wording'],j['role']):json.loads(j['request']['user']) for j in arms}
        for wording in ('original','clarified'):
            language = payloads[(wording,'language')].copy()
            evidence = payloads[(wording,'evidence')].copy()
            assert language.pop('computed_scene_facts') is None
            assert evidence.pop('computed_scene_facts')
            assert language == evidence
        for role in ('language','evidence'):
            old = payloads[('original',role)].copy()
            new = payloads[('clarified',role)].copy()
            assert new.pop('instruction').replace(audit.NEW,audit.OLD) == old.pop('instruction')
            assert old == new
        assert all(set(p)=={'instruction','scene','candidate_policy','computed_scene_facts'} for p in payloads.values())


def test_diagnostic_never_relabels_official_failures(tmp_path):
    out = tmp_path/'diagnostic'
    result = audit.prepare(out)
    rows = audit.fair.base.read(out/'failure_diagnosis.json')
    assert len(rows)==12 and all(r['official_status']=='SCHEMA_FAILED' for r in rows)
    assert sum(r['alternate_decision_agrees_with_gold'] is True for r in rows)==9
    assert result['official_scores_unchanged']
