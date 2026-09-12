"""Equal-definition three-arm runner; reuse frozen ledger and independent replay engine."""
import argparse
from contextlib import contextmanager
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import scene_rule30_run as base
from scripts.scene_haiku_contract import contracted_request
from scripts.scene_rule30_glossary import GLOSSARY
from scripts.scene_glossary_http1 import CurlLLM

DATA = ROOT/'data/scene_fair30_candidate'


def request(case, role, candidate=None):
    payload = contracted_request(case, role, candidate)
    payload['system'] += GLOSSARY
    return payload


@contextmanager
def configured():
    old_data, old_request = base.DATA, base.request
    base.DATA, base.request = DATA, request
    try:
        yield
    finally:
        base.DATA, base.request = old_data, old_request


def prepare(run, mode='REAL', receipt=None):
    with configured():
        base.prepare(run, concurrency=2, mode=mode)
    config = base.read(run/'config.json')
    config['transport'] = 'curl_http1'
    base.write(run/'config.json', config)
    manifest = base.read(run/'manifest.json')
    manifest.update(protocol='scene-fair30-v1', scope='UNREVIEWED_DEVELOPMENT_ONLY' if mode=='REAL' else 'MOCK_ENGINEERING_ONLY',
        authorization='用户：按照统一DSL定义和新案例的建议推进。语义审阅完成后才采集。',
        prompt_revision='same-glossary-all-three-arms-v1', max_recoveries=18,
        stopping='At most198 physical attempts, at most2 per call, concurrency2. Stop401/403/429; no semantic or schema retries.',
        dataset_manifest_sha256=base.digest(DATA/'manifest.json'))
    manifest['files']['config.json'] = base.digest(run/'config.json')
    for name in ('scripts/scene_fair30.py', 'scripts/prepare_scene_fair30.py',
                 'scripts/prepare_scene_rule30.py', 'scripts/scene_rule30_glossary.py', 'scripts/scene_glossary_http1.py'):
        target = run/'source'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, target)
        manifest['sources'][name] = base.digest(target)
    if receipt is not None:
        shutil.copyfile(receipt, run/'human_review_receipt.json')
        manifest['files']['human_review_receipt.json'] = base.digest(run/'human_review_receipt.json')
    base.write(run/'manifest.json', manifest)
    base.verify(run)


def require_review(run):
    manifest = base.verify(run)
    if manifest['mode'] != 'REAL':
        return
    name = 'human_review_receipt.json'
    if name not in manifest['files']:
        raise ValueError('Human semantic review PENDING; no API request launched')
    receipt = base.read(run/name)
    expected = {c['case_id'] for c in base.read(run/'model_inputs.json')}
    if (receipt.get('status') != 'APPROVED' or not receipt.get('reviewer') or not receipt.get('reviewed_at')
        or not receipt.get('approval_evidence')
        or receipt.get('dataset_manifest_sha256') != manifest['dataset_manifest_sha256']
        or set(receipt.get('approved_case_ids', [])) != expected):
        raise ValueError('Review receipt must document actual approval for this exact dataset and all30 cases')


def collect(run):
    require_review(run)
    with configured():
        base.collect(run, client_factory=CurlLLM)


def audit(run):
    with base.NetworkBlocker(), configured():
        summary = base.replay(run)
        assert summary == base.read(run/'summary.json')
        physical = [base.read(p) for p in (run/'attempts').glob('*.json')]
        model = base.read(run/'config.json')['model']
        for r in physical:
            if base.read(run/'manifest.json')['mode'] == 'REAL' and r['status'] in ('COMPLETE', 'SCHEMA_FAILED'):
                assert r.get('provider_response'), 'missing provider response'
            if r.get('provider_response'):
                provider = r['provider_response']
                assert provider['model'] == model
                assert ''.join(b.get('text', '') for b in provider['content'] if isinstance(b, dict)) == r['raw_response']
        if base.read(run/'manifest.json')['mode'] == 'REAL':
            require_review(run)
        # Core replay intentionally reports PENDING; actual signed review evidence lives separately.
        base.write(run/'audit.json', dict(status='PASS_OFFLINE', scope=summary['scope'],
            independent_decisions=summary['independent_decisions_verified'], logical_units=summary['logical_units'],
            review_receipt_present=(run/'human_review_receipt.json').exists(),
            raw_task_success={role:sum(r['role']==role and r['status']=='COMPLETE' and r['object_success'] for r in summary['rows']) for role in base.ROLES}))
        base.write(run/'delivery_integrity.json', {str(p.relative_to(run)):base.digest(p) for p in run.rglob('*')
            if p.is_file() and p.name != 'delivery_integrity.json'})
        return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('prepare', 'collect', 'mock', 'replay'))
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--review-receipt', type=Path)
    a = p.parse_args()
    if a.action == 'prepare':
        prepare(a.run_dir, receipt=a.review_receipt)
    elif a.action == 'mock':
        prepare(a.run_dir, mode='MOCK')
        with base.NetworkBlocker():
            collect(a.run_dir)
        print(audit(a.run_dir)['scope'])
    elif a.action == 'collect':
        collect(a.run_dir)
        print(audit(a.run_dir)['methods'])
    else:
        print(audit(a.run_dir)['methods'])
