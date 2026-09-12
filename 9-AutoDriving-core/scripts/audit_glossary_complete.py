"""Offline audit including all archived physical attempts, deduplicating inherited files."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import scene_rule30_glossary as g


def audit(run):
    with g.base.NetworkBlocker():
        summary = g.replay(run)
        assert summary == g.base.read(run / 'summary.json'), 'summary differs'
        continuation = g.base.read(run / 'continuation.json')
        for name, digest in continuation['inherited_answers'].items():
            assert g.base.digest(run / 'attempts' / name) == digest, 'inherited response changed'
        unique = {}
        for path in run.rglob('attempts/*.json'):
            unique[g.base.digest(path)] = g.base.read(path)
        plan = {j['call_id']: j for j in g.base.read(run / 'plan.json')}
        model = g.base.read(run / 'config.json')['model']
        terminal = []
        for record in unique.values():
            assert record['source'] == 'REAL'
            assert record['request'] == plan[record['call_id']]['request']
            assert record['status'] in g.TERMINAL | {'TRANSPORT_FAILED'}
            if record['status'] in g.TERMINAL:
                provider = record['provider_response']
                assert provider['model'] == model
                assert ''.join(b.get('text', '') for b in provider['content'] if isinstance(b, dict)) == record['raw_response']
                terminal.append(record)
        assert len(terminal) == len({r['call_id'] for r in terminal}) == 60
        failures = len(unique) - len(terminal)
        assert len(unique) == summary['physical_calls'] + continuation['previous_transport_failures']
        assert len(unique) <= continuation['combined_budget']
        old = {r['call_id']: r for r in g.base.read(run / 'reference_summary.json')['rows']}
        discordant = []
        for row in summary['rows']:
            evidence = old[f"{row['case_id']}__r{row['rep']}__evidence"]
            if row['object_success'] != evidence['object_success']:
                discordant.append(dict(case_id=row['case_id'], rep=row['rep'], block_id=row['block_id'],
                    glossary_correct=row['object_success'], evidence_correct=evidence['object_success']))
        report = dict(status='PASS_OFFLINE_MATCHED_CONTROL', human_review='PENDING',
            independent_decisions=60, unchanged_inherited_answers=len(continuation['inherited_answers']),
            combined_physical_calls=len(unique), combined_transport_failures=failures,
            usage_unknown_failures=failures, valid_response_tokens=summary['cost'],
            glossary_vs_evidence_discordant=discordant)
        g.base.write(run / 'combined_audit.json', report)
        g.base.write(run / 'delivery_integrity.json', {
            str(f.relative_to(run)): g.base.digest(f) for f in sorted(run.rglob('*'))
            if f.is_file() and f.name != 'delivery_integrity.json'})
        return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(audit(args.run))
