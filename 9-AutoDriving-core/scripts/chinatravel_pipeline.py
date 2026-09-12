"""Bounded official-Act integration smoke and offline official evaluation.
This is an adapted integration baseline, not a DARC or published benchmark result.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import socket
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / '9-AutoDriving-core'
UPSTREAM = ROOT / 'external/ChinaTravel'
# Import names are deliberately unambiguous; never import `baselines`.
sys.path.insert(0, str(CORE / 'src'))
sys.path.insert(0, str(UPSTREAM))


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextlib.contextmanager
def offline():
    from unittest.mock import patch
    def blocked(*args, **kwargs):
        raise RuntimeError('Network prohibited during evaluation/replay')
    with patch.object(socket.socket, 'connect', blocked), patch.object(socket, 'create_connection', blocked), patch.object(socket.socket, 'connect_ex', blocked):
        yield


def model_input(record):
    # Only original query reaches the agent. No structured labels/DSL/metadata.
    text = record['nature_language']
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Missing original natural-language query')
    return {'uid': record['uid'], 'nature_language': text}


def evaluate(queries, predictions):
    """Same three official functions and intersection as eval_exp.py.
    All expected IDs are retained; missing/malformed predictions become {}.
    """
    if not queries or set(predictions) - set(queries):
        raise ValueError('Empty query set or unexpected prediction IDs')
    ids = sorted(queries)
    plans = {uid: predictions.get(uid) if isinstance(predictions.get(uid), dict) else {} for uid in ids}
    with offline():
        from chinatravel.evaluation.schema_constraint import evaluate_schema_constraints
        from chinatravel.evaluation.commonsense_constraint import evaluate_commonsense_constraints
        from chinatravel.evaluation.hard_constraint import evaluate_hard_constraints_v2
        schema = read(UPSTREAM / 'chinatravel/evaluation/output_schema.json')
        s, sf, sp = evaluate_schema_constraints(ids, plans, schema)
        cm, ci, cf, cp = evaluate_commonsense_constraints(ids, queries, plans, verbose=False, lang='zh')
        hm, hi, chm, chi, hf, hp = evaluate_hard_constraints_v2(ids, queries, plans, env_pass_id=cp, verbose=False, lang='zh')
    return dict(n_expected=len(ids), ids=ids, schema_rate=s, commonsense_macro=cm,
                commonsense_micro=ci, hard_macro=hm, hard_micro=hi,
                conditional_hard_macro=chm, conditional_hard_micro=chi,
                all_pass_ids=sorted(set(sp) & set(cp) & set(hp)),
                all_pass_rate=100 * len(set(sp) & set(cp) & set(hp)) / len(ids),
                schema=sf.to_dict('records'), commonsense=cf.to_dict('records'), hard=hf.to_dict('records'))


class BudgetStop(RuntimeError):
    pass


class Bridge:
    """Adapt the project LLM.complete interface to official Act's text protocol.
    Persist every request before transport and every response immediately.
    """
    def __init__(self, client, directory, max_calls=12, max_seconds=900, max_chars=160000):
        self.client, self.directory = client, Path(directory)
        self.max_calls, self.max_seconds, self.max_chars = max_calls, max_seconds, max_chars
        self.started = time.monotonic()
        self.calls = 0
        self.total_chars = 0
        self.input_token_count = self.output_token_count = self.input_token_maxx = 0
        self.invalid_streak = 0

    def __call__(self, messages, one_line=True, json_mode=False):
        if self.calls >= self.max_calls or time.monotonic() - self.started >= self.max_seconds:
            raise BudgetStop('Call/time budget reached')
        user = json.dumps(messages, ensure_ascii=False)
        if self.total_chars + len(user) > self.max_chars:
            raise BudgetStop('Cumulative request character budget reached')
        system = ('You are connected to a REAL local ChinaTravel sandbox through a text command executor. '
                  'The host executes the single Python-style tool call you output and returns its observation. '
                  'These tools do not require native API tool/function declarations. Use only the documented tools. '
                  'Treat the JSON below as the accumulated conversation, including actual tool observations. '
                  'Preserve the original user requirements. Do not invent sandbox entities or values. ')
        system += ('Return exactly one single-line tool call, without prose or code fences.' if one_line else
                   'Return only the final JSON plan object with itinerary/activities, following the supplied official schema.')
        self.calls += 1
        self.total_chars += len(user)
        path = self.directory / f'call_{self.calls:03d}.json'
        record = {'system': system, 'user': user, 'one_line': one_line, 'json_mode': json_mode}
        write(path, record)
        try:
            response = self.client.complete(system, user)
        except Exception as exc:
            record['error_type'] = type(exc).__name__
            write(path, record)
            raise
        record['response'] = response
        record['telemetry'] = self.client.telemetry[-1] if self.client.telemetry else None
        write(path, record)
        if one_line:
            import ast
            try:
                tree = ast.parse(response.strip(), mode='eval').body
                valid = isinstance(tree, ast.Call) and isinstance(tree.func, ast.Name)
            except SyntaxError:
                valid = False
            self.invalid_streak = 0 if valid else self.invalid_streak + 1
            if self.invalid_streak >= 2:
                raise BudgetStop('Two consecutive non-command responses')
        return response


def preflight():
    # Verify actual CSV/JSON files used by official tools, not just parquet exports.
    base = UPSTREAM / 'temp_sandbox'
    verified = {}
    for lang, folder in [('zh', 'database'), ('en', 'database_en')]:
        manifest = base / 'manifests' / f'SHA256SUMS.{lang}'
        count = 0
        for line in manifest.read_text().splitlines():
            expected, name = line.split(maxsplit=1)
            file = UPSTREAM / 'chinatravel/environment' / folder / name.lstrip('*')
            if not file.is_file() or sha(file) != expected:
                raise ValueError(f'Sandbox source mismatch: {lang}/{name}')
            count += 1
        verified[lang] = count
    return verified


def run(args):
    from dataclasses import replace
    from llm_client import LLM, resolve_config
    from chinatravel.environment.world_env import WorldEnv
    from chinatravel.agent.pure_neuro_agent.pure_neuro_agent import ActAgent
    from chinatravel.agent.pure_neuro_agent.prompts import ZEROSHOT_ACT_INSTRUCTION, DIRECT_PROMPT
    pre = preflight()
    raw = read(CORE / 'data/chinatravel_dev_60.json')
    uid = args.uid or sorted(raw)[0]
    if uid not in raw:
        raise ValueError('Only frozen dev IDs are allowed')
    public = model_input(raw[uid])
    out = Path(args.run_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    config = replace(resolve_config(args.config), json_mode=False, retries=0, timeout=60,
                     max_output_tokens=4096, max_concurrency=1)
    write(out / 'manifest.json', {'scope': 'development_single_case_integration_smoke', 'uid': uid,
          'model': config.model, 'provider': config.provider, 'base_url': config.base_url,
          'max_calls': args.max_calls, 'max_seconds': 900, 'max_request_chars_total': 160000,
          'adaptation': 'official Act with explicit text-tool bridge and bounded execution',
          'input_fields': list(public), 'oracle_translation': False, 'sandbox_verified': pre,
          'data_sha256': sha(CORE / 'data/chinatravel_dev_60.json'),
          'pipeline_sha256': sha(__file__), 'schema_sha256': sha(UPSTREAM / 'chinatravel/evaluation/output_schema.json')})
    write(out / 'public_input.json', public)
    # The gold record is used only by a separate replay process, after collection.
    client = LLM(config=config)
    bridge = Bridge(client, out / 'requests', max_calls=args.max_calls)
    schema = (UPSTREAM / 'chinatravel/evaluation/output_schema.json').read_text()
    agent = ActAgent(WorldEnv(lang='zh'), bridge, ZEROSHOT_ACT_INSTRUCTION,
                     max_steps=args.max_calls, plan_prompt=DIRECT_PROMPT + '\nOfficial JSON schema:\n' + schema,
                     debug=False)
    plan = {}
    try:
        result = agent(public['nature_language'])
        write(out / 'agent_trace.json', result['log'])
        plan = json.loads(result['ans'])
        if not isinstance(plan, dict):
            plan = {}
    except Exception as exc:
        write(out / 'failure.json', {'error_type': type(exc).__name__,
              'reason': str(exc) if isinstance(exc, BudgetStop) else 'See local request/trace records'})
        write(out / 'agent_trace.json', agent._log)
    write(out / 'predictions.json', {uid: plan})
    write(out / 'collection.json', {'calls': bridge.calls, 'request_chars_total': bridge.total_chars,
          'elapsed_seconds': time.monotonic() - bridge.started, 'has_itinerary': 'itinerary' in plan})
    files = {str(p.relative_to(out)): sha(p) for p in out.rglob('*.json')}
    write(out / 'collection_hashes.json', files)
    print(json.dumps({'run_dir': str(out), 'calls': bridge.calls, 'has_itinerary': 'itinerary' in plan}))


def replay(args):
    out = Path(args.run_dir).resolve()
    for name, digest in read(out / 'collection_hashes.json').items():
        if sha(out / name) != digest:
            raise ValueError('Collection integrity failure: ' + name)
    manifest = read(out / 'manifest.json')
    data = CORE / 'data/chinatravel_dev_60.json'
    if sha(data) != manifest['data_sha256'] or sha(__file__) != manifest['pipeline_sha256']:
        raise ValueError('Data or pipeline changed since collection')
    preflight()
    raw = read(data)
    uid = manifest['uid']
    predictions = read(out / 'predictions.json')
    if set(predictions) != {uid}:
        raise ValueError('Missing/extra prediction IDs')
    with offline(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        score = evaluate({uid: raw[uid]}, predictions)
    prior = out / 'official_score.json'
    if prior.exists() and read(prior) != score:
        raise ValueError('Replay differs from prior score')
    write(prior, score)
    print(json.dumps({k: score[k] for k in ['n_expected', 'schema_rate', 'commonsense_macro', 'hard_macro', 'all_pass_rate']}))


def main():
    p = argparse.ArgumentParser(__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    r = sub.add_parser('run'); r.add_argument('--uid'); r.add_argument('--config', required=True)
    r.add_argument('--run-dir', required=True); r.add_argument('--max-calls', type=int, default=12)
    e = sub.add_parser('replay'); e.add_argument('--run-dir', required=True)
    a = p.parse_args()
    if a.command == 'run':
        if not 1 <= a.max_calls <= 16: p.error('max-calls must be 1..16 for integration smoke')
        run(a)
    else: replay(a)

if __name__ == '__main__': main()
