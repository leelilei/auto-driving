"""Offline development audit, including independent reference execution and cache usage."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import scene_pilot12 as s
from scripts.prepare_scene_pilot12 import solve
from src.scene_policy import parse_response

def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args();run=args.run
    with s.NetworkBlocker():
        result=s.replay(run,save=False)
        assert json.loads(json.dumps(result))==s.read(run/'summary.json')
        public={v['case_id']:v for v in s.read(run/'model_inputs.json')}
        gold={v['case_id']:v for v in s.read(run/'gold_and_traces.json')}
        independent=0
        for row in result['rows']:
            scene=public[row['case_id']]['scene']
            assert scene['speed_units_per_minute']==1, 'reference solver only supports these fixed speed fixtures'
            if row['policy'] is not None:
                ref=solve(scene,row['policy'])
                assert row['decision']==dict(status=ref['status'],selected_poi_ids=sorted(ref['accepted_poi_ids']))
                independent+=1
            record=s.resolve(run,row['call_id'])
            if record['status']=='COMPLETE':
                assert parse_response(record['raw_response'])[0].to_dict()==record['parsed_policy']
                assert record['provider_response']['model']==s.read(run/'config.json')['model']
            if 'request' in record:
                user=json.loads(record['request']['user'])
                assert set(user)<= {'instruction','scene','candidate_policy','computed_scene_facts'}
                assert user['instruction']==public[row['case_id']]['instruction']
                assert user['scene']==scene
        for cid,g in gold.items():
            ref=solve(public[cid]['scene'],g['policy'])
            assert ref['status']==g['status'] and ref['accepted_poi_ids']==g['accepted_poi_ids']
        costs={}
        for role in s.ROLES:
            records=[s.read(f) for f in (run/'attempts').glob('*.json') if s.read(f)['role']==role and s.read(f)['status']!='UPSTREAM_SCHEMA_FAILED']
            usage=[r['provider_response']['usage'] for r in records if r.get('provider_response',{}).get('usage') is not None]
            fields=('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')
            sums={field:sum(u.get(field,0) for u in usage) for field in fields}
            costs[role]=dict(physical_attempts=len(records),provider_usage_records=len(usage),**sums,
                 total_including_cache=sum(sums.values()),
                 reported_total_excludes_cache_warning='Main summary tokens omit Anthropic cache fields; use this breakdown. No price assumed.')
        disagreements=[]
        index={r['call_id']:r for r in result['rows']}
        for cid in public:
            for rep in (1,2):
                rows={role:index[f'{cid}__r{rep}__{role}'] for role in s.ROLES}
                if any(not r['rule_correct'] or not r['object_success'] for r in rows.values()):
                    disagreements.append(dict(case_id=cid,rep=rep,gold_policy=gold[cid]['policy'],
                         methods={role:{k:r[k] for k in ('policy','decision','rule_correct','object_success','corrected','damaged')} for role,r in rows.items()}))
        audit=dict(status='PASS_OFFLINE_ENGINEERING_AUDIT',research_status='UNREVIEWED_DEVELOPMENT_ONLY',
              full_summary_replay_equal=True,independent_prediction_executions=independent,
              human_review='PENDING',methods=result['methods'],cost_including_cache=costs,
              disagreements=disagreements,source_sha256=s.digest(Path(__file__)),
              reference_source_sha256=s.digest(ROOT/'scripts/prepare_scene_pilot12.py'))
        s.write(run/'independent_audit.json',audit)
        s.write(run/'delivery_integrity.json',{str(f.relative_to(run)):s.digest(f) for f in sorted(run.rglob('*.json')) if f.name!='delivery_integrity.json'})
        print(json.dumps({k:v for k,v in audit.items() if k!='disagreements'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
