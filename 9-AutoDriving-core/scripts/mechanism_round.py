"""Frozen 24-case injected-candidate diagnostic; not a natural-error benchmark."""
import argparse
import copy
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.collect_v5_diagnostic import execute_call, render, stamp
from scripts.experiment_v5 import record_intent, weight_direction
from src.evaluation import compare_intents, check_route
from src.graph import SyntheticGraph
from src.intent import Intent, closure
from src.llm_client import LLM, load_config
from src.solver import ExactRouteSolver
from src.v5.contrast import build_contrast_report, differing_fields, intent_dict

RUN = ROOT / 'results/v5/diagnostic/20260910_controlled_mechanism24'
CONFIG = ROOT / 'configs/v5/deepseek_official_v41_flash_preview.json'

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def scores(value, gold, graph):
    if value is None:
        return dict(hard=False, direction=False, correct=False, tsr=False)
    hard = compare_intents(value, gold)['hard_exact']
    direction = weight_direction(value.quality_weight) == weight_direction(gold.quality_weight)
    route = ExactRouteSolver(graph).solve(**value.solver_args())
    return dict(hard=hard, direction=direction, correct=hard and direction,
                tsr=check_route(graph, route, gold)['task_success'])

def prepare():
    if RUN.exists():
        raise RuntimeError('refuse to replace frozen experiment')
    source = ROOT / 'data/pilot/pilot_80_utterances.json'
    admission = ROOT / 'results/v5/development/pilot8_review_admission.json'
    assert json.loads(admission.read_text())['collection_allowed']
    data = {r['group_id']: r for r in json.loads(source.read_text()) if r['variant_type'] == 'V0'}
    specs = [('missing_deadline', [1,4,6,7]), ('reversed_order', [1,2,5,6]),
             ('extra_order', [3,4,7,8]), ('reversed_preference', [1,5,6,7]),
             ('both_correct', [2,3,4,8]), ('common_error', [1,2,5,6])]
    RUN.mkdir(parents=True)
    (RUN / 'attempts').mkdir()
    cases, jobs = [], []
    inputs = {str(source.relative_to(ROOT)): digest(source), str(admission.relative_to(ROOT)): digest(admission),
              str(CONFIG.relative_to(ROOT)): digest(CONFIG), str(Path(__file__).relative_to(ROOT)): digest(Path(__file__))}
    for family, ids in specs:
        for index, n in enumerate(ids):
            gid = f'pilot_{n:02d}'
            row = data[gid]
            gold = record_intent(row)
            good = intent_dict(gold)
            bad = copy.deepcopy(good)
            if family == 'missing_deadline':
                assert bad['time_limit'] is not None
                bad['time_limit'] = None
            elif family in ('reversed_order', 'common_error'):
                assert bad['dependencies']
                bad['dependencies'][0] = bad['dependencies'][0][::-1]
            elif family == 'extra_order':
                reach = closure(gold.dependencies)
                pairs = [(a,b) for a in sorted(gold.pois) for b in sorted(gold.pois)
                         if a != b and (a,b) not in reach and (b,a) not in reach]
                bad['dependencies'].append(list(pairs[0]))
            elif family == 'reversed_preference':
                bad['quality_weight'] = 1 - bad['quality_weight']
            a,b = (good,bad) if index % 2 == 0 else (bad,good)
            if family == 'common_error':
                a,b = bad,bad
            if family == 'both_correct':
                a,b = good,good
            a,b = Intent.parse(a), Intent.parse(b)
            graph_path = ROOT / f'results/v5/development/20260909_s1_graphs_v3/{gid}/tradeoff.json'
            inputs[str(graph_path.relative_to(ROOT))] = digest(graph_path)
            graph = SyntheticGraph.load(graph_path)
            report = build_contrast_report(row['text'], a,b,graph)
            cid = f'{family}_{index+1}'
            baseline = scores(a,gold,graph)
            assert scores(gold,gold,graph)['tsr']
            assert scores(a,gold,graph)['correct'] + scores(b,gold,graph)['correct'] == (2 if family=='both_correct' else 0 if family=='common_error' else 1)
            cases.append(dict(id=cid, family=family, source_group=gid, instruction=row['text'],
                              gold=good, a=intent_dict(a), b=intent_dict(b), graph=str(graph_path.relative_to(ROOT)),
                              baseline=baseline, report=report))
            for role, prompt in [('fields','review_fields'),('darc','review_darc')]:
                path = ROOT / f'prompts/v5/{prompt}.txt'
                inputs[str(path.relative_to(ROOT))] = digest(path)
                user = render(path.read_text(), instruction=row['text'], candidate_a=intent_dict(a),
                              candidate_b=intent_dict(b), field_differences={'fields':differing_fields(a,b)},
                              decision_contrast_report=report)
                jobs.append(dict(id=f'{cid}__{role}', case=cid, role=role, system='Return only the requested JSON object.', user=user))
    dump(RUN/'cases.json',cases)
    dump(RUN/'requests.json',jobs)
    dump(RUN/'manifest.json',dict(created=stamp(), scope='author_injected_candidates_development_only',
         human_review='source instructions previously admitted; injected candidates author constructed, not human signed',
         planned_calls=48, model=json.loads(CONFIG.read_text())['model'], retries=0, concurrency=4,
         max_output_tokens=1600, primary='paired semantic correctness darc minus fields; hard and direction jointly',
         secondary='TSR, correction and damage relative to A; raw and fallback separately',
         limitations='24 cases reuse 8 source groups; no significance claim; no natural error prevalence; no exact-weight truth',
         continuation='descriptive evidence only; ties do not support expansion; do not tune prompts or samples after results',
         inputs=inputs, cases_sha256=digest(RUN/'cases.json'), requests_sha256=digest(RUN/'requests.json')))
    print('FROZEN: 24 cases, 48 requests; all candidate invariants and gold route feasibility passed', flush=True)

def verify():
    m=json.loads((RUN/'manifest.json').read_text())
    for p,h in m['inputs'].items():
        assert digest(ROOT/p)==h, p
    for p in ['cases','requests']:
        assert digest(RUN/f'{p}.json')==m[f'{p}_sha256']

def collect():
    verify()
    config=replace(load_config(CONFIG), retries=0, max_concurrency=1, max_output_tokens=1600)
    jobs=json.loads((RUN/'requests.json').read_text())
    def work(job):
        path=RUN/'attempts'/f"{job['id']}.json"
        return execute_call(LLM(config),path,job['id'],job['role'],job['system'],job['user'],'tradeoff')
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,f in enumerate(as_completed([pool.submit(work,j) for j in jobs]),1):
            r=f.result()
            print(i,r['call_id'],r['status'],flush=True)
    analyze()

def analyze():
    verify()
    cases=json.loads((RUN/'cases.json').read_text())
    records={p.stem:json.loads(p.read_text()) for p in (RUN/'attempts').glob('*.json')}
    expected={j['id'] for j in json.loads((RUN/'requests.json').read_text())}
    complete=set(records)==expected and all(r['status'] in ('COMPLETE','SCHEMA_FAILED') for r in records.values())
    result=dict(collection_complete=complete, recorded=len(records), planned=48,
                statuses={s:sum(r['status']==s for r in records.values()) for s in ('COMPLETE','SCHEMA_FAILED','TRANSPORT_FAILED')},
                provider_tokens=sum((r.get('telemetry') or {}).get('total_tokens',0) for r in records.values()
                                    if (r.get('telemetry') or {}).get('usage_source')=='provider'))
    if complete:
        rows=[]
        for c in cases:
            gold=Intent.parse(c['gold']); graph=SyntheticGraph.load(ROOT/c['graph'])
            for role in ('fields','darc'):
                rec=records[f"{c['id']}__{role}"]
                raw=Intent.parse(rec['parsed_intent']) if rec['status']=='COMPLETE' else None
                effective=raw or Intent.parse(c['a'])
                sc=scores(effective,gold,graph)
                rows.append(dict(case=c['id'],family=c['family'],source_group=c['source_group'],role=role,
                                 raw=scores(raw,gold,graph),effective=sc,fallback=raw is None,
                                 corrected=not c['baseline']['correct'] and sc['correct'],
                                 damaged=c['baseline']['correct'] and not sc['correct']))
        result['rows']=rows
        result['methods']={role:{'n':24,'correct':sum(r['effective']['correct'] for r in rows if r['role']==role),
                           'tsr':sum(r['effective']['tsr'] for r in rows if r['role']==role),
                           'corrected':sum(r['corrected'] for r in rows if r['role']==role),
                           'damaged':sum(r['damaged'] for r in rows if r['role']==role)} for role in ('fields','darc')}
        result['by_family']={fam:{role:sum(r['effective']['correct'] for r in rows if r['family']==fam and r['role']==role)
                                   for role in ('fields','darc')} for fam in sorted({c['family'] for c in cases})}
    dump(RUN/'summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['prepare','collect','analyze'])
    globals()[p.parse_args().action]()
