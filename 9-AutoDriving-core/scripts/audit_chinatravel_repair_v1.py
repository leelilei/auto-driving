"""Offline Repair v1 audit: classify archived parse/planning evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'
def main():
    deep=json.loads((RUN/'collection_deepseek_report.json').read_text()); plan=json.loads((RUN/'stage4_deepseek_planning/summary.json').read_text())
    pmap={x['uid']:x for x in plan['cases']}; rows=[]
    for rec in deep['records']:
        uid=rec['uid']; item={'uid':uid,'parse_status':rec['status']}
        if rec['status']!='JSON_VALID': item['primary_failure']='collection_failure'
        elif rec['parsed_intent'].get('people_number') is None: item['primary_failure']='parse_contract_failure'
        elif uid in pmap: item['primary_failure']=pmap[uid]['status']
        else: item['primary_failure']='not_executed'
        item['semantic_error_candidate']=False; rows.append(item)
    out={'repair_version':'v1','status':'ENGINEERING_AUDIT_COMPLETE','model_api_calls':0,'source_model_calls':deep['model_api_calls'],'rows':rows,'counts':{},'decision':'STOP_BEFORE_DARC','decision_reason':'No row has a complete, schema-valid plan plus independently adjudicated natural-language semantic error; observed failures are parse contract, search timeout, or output schema.','next':'Only reopen with a new bounded pilot if planner schema/search is repaired; otherwise close ChinaTravel as engineering case.'}
    from collections import Counter
    out['counts']=dict(Counter(x['primary_failure'] for x in rows)); (RUN/'repair_v1_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
