"""Offline integrity checks and isolated official-predicate witnesses."""
import contextlib
import io
import random
import tempfile
from pathlib import Path

import audit_chinatravel_semantics as audit
from chinatravel_pipeline import offline


def verify():
    base = audit.ROOT / 'docs/experiments/chinatravel_setup/semantic_audit_20260911'
    results = base / 'results'
    manifest = audit.read(results / 'manifest.json')
    for name, expected in manifest['source_hashes'].items():
        assert audit.sha(audit.ROOT / name) == expected, name
    for name, expected in audit.read(results / 'artifact_hashes.json').items():
        assert audit.sha(results / name) == expected, name
    rows = audit.read(results / 'audit.json')['rows']
    assert len(rows) == 60
    assert sorted(r['uid'] for r in rows) == manifest['expected_ids']
    for row in rows:
        for req in row['requirements']:
            assert req['quote'] in row['nature_language']
            assert all(0 <= i < row['official_constraint_count'] for i in req['dsl_indices'])
    selected = audit.read(results / 'selected_dev10.json')['cases']
    assert audit.select(rows) == selected
    for seed in range(10):
        shuffled = list(rows)
        random.Random(seed).shuffle(shuffled)
        assert audit.select(shuffled) == selected
    public = audit.read(results / 'public_inputs_dev10.json')
    assert len(public) == 10
    assert [r['uid'] for r in public] == [r['uid'] for r in selected]
    originals = {r['uid']: r['nature_language'] for r in rows}
    for item in public:
        assert set(item) == {'uid', 'nature_language'}
        assert item['nature_language'] == originals[item['uid']]
    with tempfile.TemporaryDirectory() as temp:
        regenerated = Path(temp) / 'results'
        with contextlib.redirect_stdout(io.StringIO()):
            audit.run(regenerated)
        for name in ('audit.json', 'selected_dev10.json', 'public_inputs_dev10.json', 'manifest.json'):
            assert audit.read(regenerated / name) == audit.read(results / name), name
        assert (regenerated / 'AUDIT_60.md').read_text() == (results / 'AUDIT_60.md').read_text()

    from chinatravel.symbol_verification.hard_constraint import evaluate_constraints_py

    def query(uid):
        return audit.read(audit.UPSTREAM / 'chinatravel/data/dev_split' / (uid + '.json'))

    witnesses = []

    def witness(uid, index, plan, expected, interpretation):
        clause = query(uid)['hard_logic_py'][index]
        actual = evaluate_constraints_py([clause], plan)
        assert actual == [expected], (uid, actual)
        witnesses.append(dict(uid=uid, clause_index=index, clause=clause,
                              synthetic_plan=plan, official_result=actual[0],
                              interpretation=interpretation))

    modes = ['metro'] + ['taxi'] * 9
    transport_plan = {'itinerary': [{'activities': [
        {'transports': [{'mode': mode}]} for mode in modes]}]}
    witness('e20241028160842228543', 3, transport_plan, True,
            'One metro occurrence among ten transport activities passes; no majority is required.')
    witness('e20241028160842228543', 3,
            {'itinerary': [{'activities': [{'transports': [{'mode': 'taxi'}]}]}]}, False,
            'Negative control: taxi only does not satisfy metro occurrence.')
    for cost, expected in ((800, True), (1002, False)):
        witness('e20241028160857444675', 3,
                {'people_number': 2, 'itinerary': [
                    {'activities': [{'type': 'accommodation', 'cost': cost}]}, {'activities': []}]},
                expected, 'Hotel total divided by two people and one night; threshold 500 per person-night.')
    omitted = query('h20241029143450090032')
    assert '预算4000' in omitted['nature_language']
    assert not audit.dsl_indices(omitted, 'budget')
    assert len(omitted['hard_logic_py']) == 3
    assert not any('cost' in code or '4000' in code for code in omitted['hard_logic_py'])
    conflict = query('h20241029143500599951')
    assert '旅行天数5' in conflict['nature_language'] and '旅游一周' in conflict['nature_language']
    for days in (5, 7):
        witness(conflict['uid'], 3, {'itinerary': [{'activities': []} for _ in range(days)]}, days == 5,
                'Gold duration is five days despite the one-week prose; source conflict remains unresolved.')
    report = {
        'status': 'passed', 'model_api_calls': 0, 'socket_network_blocked': True,
        'verified_cases': 60, 'selected_cases': 10, 'selection_shuffle_checks': 10,
        'source_hash_count': len(manifest['source_hashes']),
        'artifact_hashes_verified': True, 'regeneration_semantically_identical': True,
        'public_inputs_only_original_text_and_uid': True,
        'explicit_budget_omission': {'uid': omitted['uid'], 'clauses': omitted['hard_logic_py']},
        'predicate_witnesses': witnesses,
        'limitations': 'Isolated synthetic predicate checks, not valid travel plans, model trials, independent annotation review, or DARC evidence.',
        'verification_script_sha256': audit.sha(Path(__file__)),
    }
    audit.dump(base / 'verification.json', report)
    print('PASS: 60 source records, source/artifact hashes, regeneration, 10 fixed inputs, 6 predicate witnesses; zero model calls.')


if __name__ == '__main__':
    with offline():
        verify()
