"""Offline failure diagnosis and frozen 2x2 interface experiment requests; no collection."""
import argparse
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import scene_fair30 as fair
from src.scene_policy import Policy, decode_response_object

REFERENCE = ROOT/'results/scene_fair30/20260910T163441Z_haiku_reviewed'
OLD = 'If no pharmacy can satisfy every requirement, report INFEASIBLE.'
NEW = ('If no pharmacy can satisfy every requirement, the downstream executor reports INFEASIBLE. '
       'Your task is only to extract the requested rule fields; preserve those rules even when no pharmacy is feasible.')


def clarified(case):
    if case['instruction'].count(OLD) != 1:
        raise ValueError('Expected exactly one frozen task sentence')
    out = deepcopy(case)
    out['instruction'] = out['instruction'].replace(OLD, NEW)
    return out


def prepare(out):
    if out.exists():
        raise ValueError('Refuse overwrite')
    with fair.base.NetworkBlocker(), fair.configured():
        original = fair.base.replay(REFERENCE)
        assert original == fair.base.read(REFERENCE/'summary.json')
    public = fair.base.read(REFERENCE/'model_inputs.json')
    gold = {c['case_id']:c for c in fair.base.read(REFERENCE/'gold_and_traces.json')}
    records = [fair.base.read(p) for p in (REFERENCE/'attempts').glob('*.json')]
    failures = []
    for record in records:
        if record['status'] != 'SCHEMA_FAILED':
            continue
        item = dict(call_id=record['call_id'], official_status='SCHEMA_FAILED',
                    diagnostic_only=True, original_error=record['error'])
        try:
            parsed = decode_response_object(record['raw_response'])
        except ValueError:
            item.update(kind='not_one_json_object', alternate_decision_agrees_with_gold=None)
        else:
            value = parsed.get('selection')
            answer = gold[record['case_id']]
            item.update(invalid_selection=value)
            if value == 'INFEASIBLE':
                item.update(kind='decision_status_in_rule_slot', alternate_decision_agrees_with_gold=answer['status']=='INFEASIBLE')
            elif isinstance(value, str) and value.startswith('P_'):
                item.update(kind='poi_id_in_rule_slot', alternate_decision_agrees_with_gold=value in answer['accepted_poi_ids'])
            else:
                item.update(kind='other_schema_error', alternate_decision_agrees_with_gold=None)
        failures.append(item)
    plan = []
    refs = {}
    # All30 cases, first repeat only, chosen without filtering by score or failure type.
    for i, case in enumerate(public):
        direct = fair.base.latest(REFERENCE, f"{case['case_id']}__r1__direct")
        assert direct['status'] == 'COMPLETE'
        refs[direct['call_id']] = direct
        candidate = Policy.parse(direct['parsed_policy'])
        conditions = [('original', 'language'), ('original', 'evidence'), ('clarified', 'language'), ('clarified', 'evidence')]
        # Fixed cyclic ordering; no outcome-dependent order or candidate changes.
        conditions = conditions[i%4:]+conditions[:i%4]
        for wording, role in conditions:
            task = case if wording == 'original' else clarified(case)
            plan.append(dict(call_id=f"{case['case_id']}__{wording}__{role}", case_id=case['case_id'],
                candidate_source=direct['call_id'], wording=wording, role=role,
                request=fair.request(task, role, candidate)))
    out.mkdir(parents=True)
    fair.base.write(out/'failure_diagnosis.json', failures)
    fair.base.write(out/'request_plan.json', plan)
    fair.base.write(out/'reference_direct_records.json', refs)
    fair.base.write(out/'original_model_inputs.json', public)
    fair.base.write(out/'clarified_model_inputs.json', [clarified(c) for c in public])
    fair.base.write(out/'gold_for_offline_scoring_only.json', list(gold.values()))
    fair.base.write(out/'protocol.json', dict(stage='OFFLINE_READY_NOT_COLLECTED',model_api_calls=0,
        purpose='Diagnose instruction-contract interaction, not prove planning method novelty.',
        planned=120, cases=30, arms=4, candidate_repeat=1, concurrency=2,
        max_transport_retries=12, max_attempts_per_unit=2, max_physical_calls=132,
        old_sentence=OLD, new_sentence=NEW,
        primary='Schema-failure reduction original minus clarified within evidence; compare same difference within language.',
        secondary='Full-denominator task success raw and with fixed Direct fallback; corrected/damaged, rule accuracy, cost.',
        controls='All four arms newly collected in same run, same frozen Direct per case, no scoring/model-based selection.',
        stopping='No semantic retries; stop401/403/429 or exhausted recovery. This script does not launch collection.',
        limitation='Post-hoc mechanism diagnosis on exposed development data; fixed old candidates; one response per case per arm; does not measure fresh end-to-end performance.'))
    fair.base.write(out/'manifest.json', dict(created=fair.base.now(), reference=str(REFERENCE),
        reference_manifest_sha256=fair.base.digest(REFERENCE/'manifest.json'),
        source_sha256=fair.base.digest(Path(__file__)), model_api_calls=0,
        files={p.name:fair.base.digest(p) for p in out.iterdir() if p.is_file()}))
    return dict(planned=len(plan), failures=len(failures),
        diagnostic_alternate_decisions_correct=sum(x['alternate_decision_agrees_with_gold'] is True for x in failures),
        official_scores_unchanged=True, model_api_calls=0)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, default=ROOT/'data/fair30_interface_diagnostic_v1')
    print(prepare(p.parse_args().out))
