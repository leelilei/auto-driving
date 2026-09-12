"""Deterministically adapt and rescore archived Repair v1 raw plans."""
import contextlib
import io
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
CORE=ROOT/'9-AutoDriving-core'
SOURCE=CORE/'data/chinatravel_repair_v1_deepseek6_retry1/planning'
OUT=CORE/'data/chinatravel_repair_v1_deepseek6_retry1/postprocessed'
CANONICAL=ROOT/'external/ChinaTravel/chinatravel/data/dev_split'
sys.path.insert(0,str(CORE/'scripts'))
import chinatravel_pipeline_v3 as ct
from chinatravel_plan_schema_adapter import adapt


def main():
    if OUT.exists(): raise ValueError('Refuse overwrite: '+str(OUT))
    OUT.mkdir(); rows=[]
    for source in sorted(p for p in SOURCE.iterdir() if p.is_dir()):
        uid=source.name; raw=ct.read(source/'raw_search_return.json'); prior=ct.read(source/'summary.json')
        repaired,changes=adapt(raw)
        accepted=repaired if prior['status']=='search_success' and ct.valid_plan(repaired) else {}
        query=ct.read(CANONICAL/f'{uid}.json')
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            score=ct.json_safe(ct.v1.evaluate({uid:query},{uid:accepted}))
        case=OUT/uid;case.mkdir();ct.write(case/'raw_plan.json',raw);ct.write(case/'adapted_plan.json',repaired)
        ct.write(case/'changes.json',changes);ct.write(case/'prediction.json',accepted);ct.write(case/'official_score.json',score)
        rows.append({'uid':uid,'search_status':prior['status'],'raw_schema_valid':ct.valid_plan(raw),
                     'adapted_schema_valid':ct.valid_plan(repaired),'changes':len(changes),
                     'prediction_accepted':bool(accepted),'official_all_pass_rate':score['all_pass_rate']})
    result={'status':'REPAIR_V1_POSTPROCESS_COMPLETE','model_api_calls':0,
            'invented_values':0,'cases':rows}
    ct.write(OUT/'summary.json',result);print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
