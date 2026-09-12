"""Normalize archived plain-JSON Stage-3 responses offline."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'
sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_parse_plan_v4 as v4

def normalize(x):
    x=dict(x)
    x['room_type']={'单床房':1,'双床房':2,'single-bed room':1,'double-bed room':2}.get(x.get('room_type'),x.get('room_type'))
    x['intercity_mode']={'火车':'train','飞机':'airplane','train':'train','airplane':'airplane'}.get(x.get('intercity_mode'),x.get('intercity_mode'))
    return x

def main():
    src=json.loads((RUN/'collection_json_report.json').read_text())
    public={r['uid']:r['nature_language'] for r in json.loads((RUN/'public_inputs.json').read_text())}
    rows=[]
    for r in src['records']:
        if r['status']!='JSON_VALID':
            rows.append({'uid':r['uid'],'attribution':'collection_failure'})
            continue
        parsed=normalize(r['parsed_intent'])
        try:
            v4.validate(parsed,public[r['uid']]); v4.compile_extended(parsed); kind='planning_ready'; err=None
        except Exception as e:
            kind='contract_or_compile_failure'; err=str(e)
        row={'uid':r['uid'],'attribution':kind,'normalized_intent':parsed}
        if err: row['error']=err
        rows.append(row)
    out={'status':'STAGE4_READY_FOR_PLANNING','model_api_calls':0,'source_calls':src['model_api_calls'],'rows':rows,
         'counts':{'planning_ready':sum(r['attribution']=='planning_ready' for r in rows),
                   'contract_or_compile_failure':sum(r['attribution']=='contract_or_compile_failure' for r in rows),
                   'semantic_error':None},'stage5':'blocked_until_planning_and_adjudication'}
    (RUN/'stage4_json_attribution.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False))

if __name__=='__main__': main()
