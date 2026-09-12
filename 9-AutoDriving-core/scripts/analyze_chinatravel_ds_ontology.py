"""Offline counterfactual analysis for the two DeepSeek ontology mismatches."""
import json, re
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; CORE=ROOT/'9-AutoDriving-core'; RUN=CORE/'data/chinatravel_crossmodel100_20260912'; UP=ROOT/'external/ChinaTravel/chinatravel/data/dev_split'
sys.path.insert(0,str(CORE/'scripts')); import chinatravel_parse_plan_v4 as parser

CASES={
 'h20241029143502525564': {'field':'cuisine','raw':'重庆美食','mapped':'川菜','reason':'官方 DSL hard_logic_py 要求 restaurant_type=川菜；原句的重庆美食是自然语言地域描述。'},
 'h20241029143504074288': {'field':'attraction_category','raw':'历史人文','mapped':'人文景观','reason':'官方 DSL 接受 历史古迹 或 人文景观；原句的历史人文是较宽泛描述。'},
}
def read(p): return json.loads(Path(p).read_text())
def main():
 records={r['uid']:r for r in read(RUN/'collection_deepseek.json')['records']}
 out=[]
 for uid,spec in CASES.items():
  q=read(UP/f'{uid}.json'); pred=records[uid]['parsed_intent']; variants=[]
  for label,value in [('model_raw',spec['raw']),('null',None),('official_mapped',spec['mapped'])]:
   x=dict(pred); x[spec['field']]=value; parser.validate(x,q['nature_language']); clauses=parser.compile_extended(x)
   variants.append({'variant':label,'value':value,'compiled_clauses':clauses,'target_function':('restaurant_type' if spec['field']=='cuisine' else 'attraction_type')})
  official=[c for c in q['hard_logic_py'] if ('restaurant_type' in c if spec['field']=='cuisine' else 'attraction_type' in c)]
  out.append({'uid':uid,'nature_language':q['nature_language'],'field':spec['field'],'model_value':pred[spec['field']], 'official_clauses':official,'variants':variants,'interpretation':spec['reason'],'status':'ONTOLOGY_MISMATCH_REQUIRES_REVIEW'})
 result={'status':'PASS_OFFLINE_COUNTERFACTUAL','cases':out,'model_calls':0,'planner_calls':0,'conclusion':'Both mismatches change the compiled ontology constraint; no end-to-end score was imputed because no model plan was generated in this analysis.','next_action':'If continuing, implement an explicit ontology-aware parser contract and test it on a fresh audited slice; do not silently map values in scoring.'}
 (RUN/'ds_ontology_counterfactual.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
