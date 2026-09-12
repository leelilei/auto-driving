"""Offline Stage-4 attribution for the fixed six-case extended pilot."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'; sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_parse_plan_v4 as v4
def main():
    report=json.loads((RUN/'collection_report.json').read_text()); rows=[]
    public={r['uid']:r['nature_language'] for r in json.loads((RUN/'public_inputs.json').read_text())}
    for rec in report['records']:
        detail=None
        if rec['status']!='CONTRACT_VALID':
            kind='contract_validation_failed_raw_response_unavailable' if rec.get('error_type')=='ValueError' else 'collection_error'
            detail=rec.get('error')
        else:
            try:
                v4.validate(rec['parsed_intent'],public[rec['uid']])
            except (ValueError,TypeError,KeyError) as e:
                kind='contract_validation_failed'; detail=str(e)
            else:
                try: v4.compile_extended(rec['parsed_intent']); kind='ready_for_planning'
                except Exception as e: kind='compile_error'; detail=type(e).__name__
        rows.append({'uid':rec['uid'],'collection_status':rec['status'],'attribution':kind,'detail':detail})
    out={'status':'PENDING_PLANNING_AND_SEMANTIC_REVIEW','model_api_calls':0,'source_reported_model_api_calls':report.get('model_api_calls'),'rows':rows,
         'counts':{'ready_for_planning':sum(x['attribution']=='ready_for_planning' for x in rows),'requires_investigation':sum(x['attribution']!='ready_for_planning' for x in rows),'semantic_error':None},
         'stage5_decision':'PENDING','reason':'Planning and independent semantic adjudication are incomplete. Contract failures do not establish absence of semantic errors. Raw provider envelopes were not archived by the collector.'}
    (RUN/'stage4_final.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__': main()
