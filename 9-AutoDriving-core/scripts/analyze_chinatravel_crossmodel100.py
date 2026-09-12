"""Offline analysis of the frozen cross-model parse collection."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_crossmodel100_20260912'
AUDIT=ROOT/'docs/experiments/chinatravel_setup/semantic_audit_20260911/results/audit.json'
FIELDS=('start_city','target_city','days','people_number','budget','room_count','room_type','cuisine','intercity_mode','attraction_category')
def read(p): return json.loads(Path(p).read_text())
def main():
 rows={r['uid']:r for r in read(AUDIT)['rows']}; d=read(RUN/'collection_deepseek.json')['records']
 exact=0; mismatches=[]
 for rec in d[:60]:
  gold={x['field']:x['value'] for x in rows[rec['uid']]['requirements'] if x['field'] in FIELDS}; pred=rec['parsed_intent']; bad={f:{'expected':v,'actual':pred.get(f)} for f,v in gold.items() if pred.get(f)!=v}
  if bad: mismatches.append({'uid':rec['uid'],'fields':bad})
  else: exact+=1
 disagreements=[d[i]['uid'] for i in range(40) if d[i]['parsed_intent']!=d[60+i]['parsed_intent']]
 out={'status':'PASS','model':'deepseek-v4-flash','calls':100,'complete':sum(r['status']=='COMPLETE' for r in d),'unique_cases':60,'unique_semantic_matches_on_audited_fields':exact,'unique_semantic_mismatch_cases':len(mismatches),'mismatches':mismatches,'repeat_pairs':40,'repeat_agreement_pairs':40-len(disagreements),'repeat_disagreement_uids':disagreements,'scope':'offline parse-level diagnostic; not official all-pass and not independent 100-case coverage'}
 (RUN/'deepseek_offline_analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__': main()
