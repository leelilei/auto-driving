"""Bounded four-arm interface diagnosis with immutable requests and offline replay."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import prepare_fair30_interface_audit as design
from scripts.scene_glossary_http1 import CurlLLM
from src.llm_client import load_config
from src.scene_policy import Policy, parse_response, execute, evaluate

base = design.fair.base
DATA = ROOT/'data/fair30_interface_diagnostic_v1'
TERMINAL = {'COMPLETE', 'SCHEMA_FAILED'}


def prepare(run, mode='REAL'):
    if run.exists():
        raise ValueError('Refuse overwrite')
    dm = base.read(DATA/'manifest.json')
    for name, h in dm['files'].items():
        if base.digest(DATA/name) != h:
            raise ValueError('Changed frozen design')
    with base.NetworkBlocker(), design.fair.configured():
        old = base.replay(design.REFERENCE)
        assert old == base.read(design.REFERENCE/'summary.json')
    design.fair.require_review(design.REFERENCE)
    run.mkdir(parents=True)
    (run/'attempts').mkdir()
    for name in dm['files']:
        shutil.copyfile(DATA/name, run/name)
    shutil.copyfile(design.REFERENCE/'human_review_receipt.json', run/'human_review_receipt.json')
    shutil.copyfile(design.REFERENCE/'config.json', run/'config.json')
    names = set(base.read(design.REFERENCE/'manifest.json')['sources'])
    names.update(('scripts/run_fair30_interface.py', 'scripts/prepare_fair30_interface_audit.py'))
    sources = {}
    for name in sorted(names):
        target = run/'source'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, target)
        sources[name] = base.digest(target)
    base.write(run/'manifest.json', dict(created=base.now(), mode=mode,
        scope='POSTHOC_INTERFACE_DIAGNOSTIC' if mode=='REAL' else 'MOCK_ENGINEERING_ONLY',
        authorization='用户授权睡前长任务推进接口诊断；仅职责句澄清，原场景和gold保持已批准版本。',
        design_manifest_sha256=base.digest(DATA/'manifest.json'), reference_manifest_sha256=dm['reference_manifest_sha256'],
        files={p.name:base.digest(p) for p in run.iterdir() if p.is_file()}, sources=sources,
        planned=120, concurrency=2, max_recoveries=12, max_attempts_per_unit=2, max_physical_calls=132))
    verify(run)


def verify(run):
    m = base.read(run/'manifest.json')
    for name, h in m['files'].items():
        if base.digest(run/name) != h:
            raise ValueError('Frozen input changed: '+name)
    for name, h in m['sources'].items():
        if base.digest(ROOT/name) != h or base.digest(run/'source'/name) != h:
            raise ValueError('Source changed: '+name)
    plan = base.read(run/'request_plan.json')
    original = base.read(run/'original_model_inputs.json')
    revised = base.read(run/'clarified_model_inputs.json')
    refs = base.read(run/'reference_direct_records.json')
    if len(original)!=30 or len({c['case_id'] for c in original})!=30:
        raise ValueError('Expected30 cases')
    if revised != [design.clarified(c) for c in original]:
        raise ValueError('Unexpected instruction modification')
    expected = []
    for i,c in enumerate(original):
        source = f"{c['case_id']}__r1__direct"
        r = refs[source]
        if r['status']!='COMPLETE' or r['source']!='REAL':
            raise ValueError('Invalid historical candidate provenance')
        candidate,_ = parse_response(r['raw_response'])
        if candidate.to_dict()!=r['parsed_policy']:
            raise ValueError('Candidate parse differs')
        conditions = [('original','language'),('original','evidence'),('clarified','language'),('clarified','evidence')]
        conditions = conditions[i%4:]+conditions[:i%4]
        for wording,role in conditions:
            expected.append(dict(call_id=f"{c['case_id']}__{wording}__{role}",case_id=c['case_id'],candidate_source=source,
                wording=wording,role=role,request=design.fair.request(c if wording=='original' else revised[i],role,candidate)))
    if plan!=expected:
        raise ValueError('Plan/request mismatch')
    return m


def records(run, cid):
    return [base.read(p) for p in sorted((run/'attempts').glob(cid+'.a*.json'))]


def checkpoint(run):
    plan = base.read(run/'request_plan.json')
    pending = []
    all_records = []
    for job in plan:
        rs = records(run, job['call_id'])
        all_records.extend(rs)
        if not rs or rs[-1]['status'] not in TERMINAL:
            pending.append(dict(call_id=job['call_id'], attempts=len(rs), status=rs[-1]['status'] if rs else 'NOT_STARTED'))
    state = dict(status='COMPLETE' if not pending else 'INCOMPLETE', planned=120,
        completed=120-len(pending), pending=pending, physical_calls=len(all_records),
        transport_failures=sum(r['status']=='TRANSPORT_FAILED' for r in all_records))
    base.write(run/'checkpoint.json', state)
    return state


def mock_response(job, refs):
    return json.dumps(dict(**refs[job['candidate_source']]['parsed_policy'], evidence={}))


def collect(run):
    m = verify(run)
    plan = base.read(run/'request_plan.json')
    cfg = load_config(run/'config.json')
    refs = base.read(run/'reference_direct_records.json')
    if any(r['status']=='STARTED' for j in plan for r in records(run,j['call_id'])):
        raise ValueError('Unreconciled STARTED request; do not resample blindly')
    if m['mode']=='REAL' and not os.environ.get(cfg.api_key_env):
        key = subprocess.run(['security','find-generic-password','-s',cfg.api_key_env,'-w'],capture_output=True,text=True,check=True)
        os.environ[cfg.api_key_env]=key.stdout.strip()
    def call(job):
        seq = len(records(run,job['call_id']))+1
        path = run/'attempts'/f"{job['call_id']}.a{seq}.json"
        r = dict(**job, source=m['mode'],status='STARTED',started=base.now())
        base.write(path,r)
        client = None
        try:
            if m['mode']=='REAL':
                client = CurlLLM(cfg)
                raw = client.complete(**job['request'])
                r.update(provider_response=client.client.last_response)
            else:
                raw = mock_response(job,refs)
            r['raw_response']=raw
            policy,_ = parse_response(raw)
            r.update(status='COMPLETE',parsed_policy=policy.to_dict())
        except Exception as e:
            message = str(e)
            if os.environ.get(cfg.api_key_env):
                message = message.replace(os.environ[cfg.api_key_env],'[REDACTED]')
            r.update(status='SCHEMA_FAILED' if 'raw_response' in r else 'TRANSPORT_FAILED',error_type=type(e).__name__,error=message)
        r.update(finished=base.now(),telemetry=client.telemetry[-1] if client and client.telemetry else None)
        base.write(path,r)
        return r
    pending = [j for j in plan if not records(run,j['call_id']) or records(run,j['call_id'])[-1]['status'] not in TERMINAL]
    recoveries = sum(max(0,len(records(run,j['call_id']))-1) for j in plan)
    checkpoint(run)
    while pending:
        batch = pending[:2]
        pending = pending[2:]
        retry_count = sum(bool(records(run,j['call_id'])) for j in batch)
        if recoveries+retry_count>12 or any(len(records(run,j['call_id']))>=2 for j in batch):
            raise RuntimeError('Recovery limit reached; checkpoint preserves pending jobs')
        recoveries += retry_count
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(call,batch))
        state = checkpoint(run)
        print(f"Completed {state['completed']}/120; physical {state['physical_calls']}; failures {state['transport_failures']}",flush=True)
        for job,r in zip(batch,results):
            if r['status']=='TRANSPORT_FAILED':
                if any(f'HTTP {c}' in r.get('error','') for c in (401,403,429)):
                    raise RuntimeError('Provider refusal; stop')
                if len(records(run,job['call_id']))>=2:
                    raise RuntimeError('Unit exhausted two attempts; stop')
                pending.append(job)
    with base.NetworkBlocker():
        result = replay(run)
    base.write(run/'summary.json',result)
    audit(run)


def replay(run):
    m = verify(run)
    plan = base.read(run/'request_plan.json')
    byid = {j['call_id']:j for j in plan}
    physical = [(p,base.read(p)) for p in (run/'attempts').glob('*.json')]
    for path,r in physical:
        if r.get('call_id') not in byid or r.get('source')!=m['mode'] or path.name not in [r['call_id']+f'.a{i}.json' for i in (1,2)]:
            raise ValueError('Unexpected ledger identity')
    gold = {c['case_id']:c for c in base.read(run/'gold_for_offline_scoring_only.json')}
    scenes = {c['case_id']:c['scene'] for c in base.read(run/'original_model_inputs.json')}
    refs = base.read(run/'reference_direct_records.json')
    rows = []
    retries = 0
    for j in plan:
        rs = records(run,j['call_id'])
        retries += max(0,len(rs)-1)
        if not 1<=len(rs)<=2 or rs[-1]['status'] not in TERMINAL:
            raise ValueError('Missing or incomplete unit')
        for seq,r in enumerate(rs,1):
            if not (run/'attempts'/f"{j['call_id']}.a{seq}.json").exists() or any(r.get(k)!=v for k,v in j.items()):
                raise ValueError('Changed request or attempt sequence')
            if seq<len(rs) and r['status']!='TRANSPORT_FAILED':
                raise ValueError('Illegal semantic resampling')
        final = rs[-1]
        raw = None
        if final['status']=='COMPLETE':
            raw,_=parse_response(final['raw_response'])
            if raw.to_dict()!=final['parsed_policy']:
                raise ValueError('Saved parse mismatch')
        else:
            try:
                parse_response(final['raw_response'])
            except (ValueError,TypeError):
                pass
            else:
                raise ValueError('Valid response labelled schema failure')
        if m['mode']=='REAL':
            provider=final['provider_response']
            if provider['model']!=base.read(run/'config.json')['model'] or ''.join(b.get('text','') for b in provider['content'] if isinstance(b,dict))!=final['raw_response']:
                raise ValueError('Provider response mismatch')
        direct=Policy.parse(refs[j['candidate_source']]['parsed_policy'])
        effective=raw or direct
        decision=execute(scenes[j['case_id']],effective)
        ref=base.solve(scenes[j['case_id']],effective.to_dict())
        if decision!=dict(status=ref['status'],selected_poi_ids=sorted(ref['accepted_poi_ids'])):
            raise ValueError('Independent solver mismatch')
        score=evaluate(effective,decision,gold[j['case_id']])
        initial=evaluate(direct,execute(scenes[j['case_id']],direct),gold[j['case_id']])
        rows.append(dict(call_id=j['call_id'],case_id=j['case_id'],wording=j['wording'],role=j['role'],
            status=final['status'],policy=effective.to_dict(),decision=decision,
            schema_failed=raw is None,raw_task_success=raw is not None and score['object_success'],
            raw_rule_correct=raw is not None and score['rule_correct'],
            corrected=score['object_success'] and not initial['object_success'],damaged=initial['object_success'] and not score['object_success'],**score))
    if retries>12 or len(physical)>132:
        raise ValueError('Budget exceeded')
    fields=('schema_failed','object_success','raw_task_success','rule_correct','raw_rule_correct','corrected','damaged')
    arms={}
    for wording in ('original','clarified'):
        for role in ('language','evidence'):
            subset=[r for r in rows if r['wording']==wording and r['role']==role]
            rs=[r for _,r in physical if r['wording']==wording and r['role']==role]
            usages=[r['provider_response']['usage'] for r in rs if (r.get('provider_response') or {}).get('usage') is not None]
            sums={k:sum(u.get(k,0) for u in usages) for k in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')}
            arms[wording+'_'+role]=dict(n=len(subset),**{k:sum(r[k] for r in subset) for k in fields},
                cost=dict(physical_calls=len(rs),usage_unknown=len(rs)-len(usages),**sums,token_components_sum=sum(sums.values())))
    reductions={role:arms['original_'+role]['schema_failed']-arms['clarified_'+role]['schema_failed'] for role in ('language','evidence')}
    return dict(scope=m['scope'],complete=True,logical_units=120,physical_calls=len(physical),transport_retries=retries,
        independent_decisions=120,arms=arms,primary_schema_reduction_counts=reductions,
        difference_in_reductions=reductions['evidence']-reductions['language'],rows=rows)


def audit(run):
    with base.NetworkBlocker():
        result = replay(run)
        if result!=base.read(run/'summary.json'):
            raise ValueError('Summary differs from replay')
        base.write(run/'audit.json',dict(status='PASS_OFFLINE',scope=result['scope'],independent_decisions=120,matched_requests=120))
        base.write(run/'delivery_integrity.json',{str(p.relative_to(run)):base.digest(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='delivery_integrity.json'})
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=('prepare','collect','mock','replay'))
    p.add_argument('--run-dir',type=Path,required=True)
    a=p.parse_args()
    if a.action=='prepare':prepare(a.run_dir)
    elif a.action=='mock':
        prepare(a.run_dir,mode='MOCK')
        with base.NetworkBlocker():collect(a.run_dir)
    elif a.action=='collect':collect(a.run_dir)
    else:print(audit(a.run_dir)['arms'])
