"""Recover Claude collection with immutable per-completion checkpoints.

Preserves the original collector's prompts, parsing and bounded retry policy.
Does not use its legacy evaluator; outputs recovery_status.json separately.
"""
import argparse, fcntl, hashlib, json, threading, time
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor, as_completed
import run_full160_claude_experiment as base

REAL_LLM = base.LLM
CTX = threading.local()

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

class CheckpointLLM:
    def __init__(self, config):
        self.inner = REAL_LLM(config)
        self.client = SimpleNamespace(last_usage=None, last_response=None)
        self.indices = {}

    def complete(self, system, user):
        key = hashlib.sha256(json.dumps([system, user]).encode()).hexdigest()
        idx = self.indices.get(key, 0)
        self.indices[key] = idx + 1
        p = CTX.directory / f'{key}_{idx}.json'
        if p.exists():
            result = json.loads(p.read_text())
            assert result['system'] == system and result['user'] == user
        else:
            result = {'system': system, 'user': user, 'started': time.time()}
            try:
                result['raw'] = self.inner.complete(system, user)
                result['usage'] = getattr(self.inner.client, 'last_usage', None)
                result['response'] = getattr(self.inner.client, 'last_response', None)
            except Exception as exc:
                # Avoid persisting provider error bodies that may contain credentials.
                result['error'] = type(exc).__name__
            result['ended'] = time.time()
            base.write_json(p, result)
        self.client.last_usage = result.get('usage')
        self.client.last_response = result.get('response')
        if 'error' in result:
            raise RuntimeError('Recorded completion failure: ' + result['error'])
        return result['raw']

def collect(records, config, out):
    gid = records[0]['group_id']
    p, gp = out / (gid + '.json'), out / (gid + '_graph.json')
    if p.exists():
        existing = json.loads(p.read_text())
        assert [(u['utterance_id'],u['text']) for u in existing['utterances']] == [(u['utterance_id'],u['text']) for u in records]
        assert gp.exists()
        return gid
    if not gp.exists():
        base.generate_synthetic_graph(graph_id=gid+'_graph',seed=5000+int(gid.split('_')[-1])).save(gp)
    graph = base.SyntheticGraph.load(gp)
    solver = base.ExactRouteSolver(graph)
    rows = []
    for rec in records:
        CTX.directory = out / 'completion_checkpoints' / rec['utterance_id']
        CTX.directory.mkdir(parents=True, exist_ok=True)
        final = CTX.directory / 'utterance.json'
        if final.exists():
            row = json.loads(final.read_text())
            assert row['text'] == rec['text'] and row['utterance_id'] == rec['utterance_id']
        else:
            row = base.run_utterance(rec, graph, solver, config)
            base.write_json(final, row)
        rows.append(row)
    base.write_json(p, {'group_id':gid,'utterances_count':len(rows),'utterances':rows})
    return gid

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--run-dir',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--limit-groups',type=int,default=160)
    a = ap.parse_args()
    a.run_dir.mkdir(parents=True,exist_ok=True)
    lock = (a.run_dir / 'collector.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    dataset = base.ROOT / 'data/test/test_640_utterances.json'
    binding = {'dataset_sha256':digest(dataset),'collector_sha256':digest(Path(base.__file__)),
               'wrapper_sha256':digest(Path(__file__)),'config_sha256':digest(a.config),
               'client_sha256':digest(base.ROOT/'src/llm_client.py')}
    bp = a.run_dir / 'recovery_binding.json'
    if bp.exists():
        assert json.loads(bp.read_text()) == binding, 'Frozen recovery inputs changed'
    else:
        base.write_json(bp,binding)
    config = base.load_config(a.config)
    config = replace(config,retries=3,retry_sleep=2.0,timeout=max(config.timeout,90))
    groups = {}
    for rec in json.loads(dataset.read_text()):
        groups.setdefault(rec['group_id'],[]).append(rec)
    base.LLM = CheckpointLLM
    completed, errors = [], []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        fs = {pool.submit(collect,groups[g],config,a.run_dir):g for g in sorted(groups)[:a.limit_groups]}
        for f in as_completed(fs):
            try:
                completed.append(f.result())
            except Exception as exc:
                errors.append({'group':fs[f],'error':type(exc).__name__})
            base.write_json(a.run_dir/'recovery_status.json',{'model':config.model,'completed_groups':len(completed),'errors':errors,'updated':time.time()})
            print(f'completed={len(completed)} errors={len(errors)} latest={fs[f]}',flush=True)
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
