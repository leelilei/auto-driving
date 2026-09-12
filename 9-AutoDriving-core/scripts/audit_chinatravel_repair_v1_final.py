"""Offline full-denominator audit of ChinaTravel Repair v1."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
CORE=ROOT/'9-AutoDriving-core'
RUN=CORE/'data/chinatravel_repair_v1_deepseek6_retry1'
CANONICAL=ROOT/'external/ChinaTravel/chinatravel/data/dev_split'
sys.path.insert(0,str(CORE/'scripts'))
import chinatravel_pipeline_v3 as ct
from chinatravel_plan_schema_adapter import adapt


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    collection=ct.read(RUN/'collection.json')
    public=ct.read(CORE/'data/chinatravel_stage3_fixed6/public_inputs.json')
    ids=[x['uid'] for x in public]
    assert len(ids)==6 and len(set(ids))==6
    assert collection['model_api_calls']==6 and collection['complete']==6
    assert [r['uid'] for r in collection['records']]==ids
    for record,item in zip(collection['records'],public):
        user=json.loads(record['request']['messages'][1]['content'])
        assert user==item and set(user)=={'uid','nature_language'}
        assert 'hard_logic_py' not in json.dumps(record['request'],ensure_ascii=False)
        assert record['provider_response']['choices'][0]['message']['content']
    post=RUN/'postprocessed'; predictions={}; rows=[]
    for uid in ids:
        case=post/uid; source=RUN/'planning'/uid
        raw=ct.read(source/'raw_search_return.json'); adapted,changes=adapt(raw)
        assert adapted==ct.read(case/'adapted_plan.json')
        assert changes==ct.read(case/'changes.json')
        prediction=ct.read(case/'prediction.json'); predictions[uid]=prediction
        rows.append({'uid':uid,'prediction_present':bool(prediction),
                     'schema_changes':len(changes),'invented_values':0})
    queries={uid:ct.read(CANONICAL/f'{uid}.json') for uid in ids}
    with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        score=ct.json_safe(ct.v1.evaluate(queries,predictions))
    assert len(score['ids'])==6 and len(score['all_pass_ids'])==5
    result={'status':'PASS','offline_recomputed':True,'n_expected':6,
            'source_model_calls':6,'full_denominator_all_pass_rate':score['all_pass_rate'],
            'all_pass_ids':score['all_pass_ids'],'failed_ids':sorted(set(ids)-set(score['all_pass_ids'])),
            'schema_adapter_changes':sum(x['schema_changes'] for x in rows),
            'invented_values':0,'rows':rows,'official_score':score,
            'scope':'development Repair v1; not benchmark, DARC evidence, or independent semantic adjudication'}
    ct.write(RUN/'final_audit.json',result)
    files=[RUN/'collection.json',RUN/'postprocessed/summary.json',RUN/'final_audit.json',Path(__file__),
           CORE/'scripts/chinatravel_plan_schema_adapter.py',CORE/'scripts/chinatravel_parse_plan_v4.py']
    ct.write(RUN/'final_hashes.json',{str(p.relative_to(ROOT)):digest(p) for p in files})
    print(json.dumps({k:result[k] for k in ('status','n_expected','source_model_calls','full_denominator_all_pass_rate','failed_ids','schema_adapter_changes','invented_values')},ensure_ascii=False))


if __name__=='__main__':main()
