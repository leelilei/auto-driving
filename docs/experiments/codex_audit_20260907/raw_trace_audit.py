"""Reparse main-run raw text and resolve cached candidate routes without network."""
from pathlib import Path
import json,sys
from dataclasses import asdict
BASE=Path(__file__).resolve().parents[3];CORE=BASE/'9-AutoDriving-core';sys.path.insert(0,str(CORE))
from src.intent import Intent
from src.graph import SyntheticGraph
from src.solver import ExactRouteSolver
run=CORE/'results/runs/20260906T051339Z_main_test'
counts={'raw_candidates_checked':0,'routes_checked':0};issues=[]
canon=lambda x:json.loads(json.dumps(x))
for p in sorted(run.glob('test_*.json')):
 if p.name.endswith('_graph.json'):continue
 group=json.loads(p.read_text());solver=ExactRouteSolver(SyntheticGraph.load(run/f"{group['group_id']}_graph.json"))
 for u in group['utterances']:
  for name,c in u['calls'].items():
   if not c.get('schema_valid'):continue
   try:candidate=Intent.parse(json.loads(c['raw_response']))
   except Exception as exc:issues.append([u['utterance_id'],name,'parse',type(exc).__name__]);continue
   counts['raw_candidates_checked']+=1
   if canon(asdict(candidate))!=u['candidates'].get(name):issues.append([u['utterance_id'],name,'candidate_mismatch'])
   if name in u['routes'] and u['routes'][name]:
    fresh=solver.solve(**candidate.solver_args());counts['routes_checked']+=1
    saved=u['routes'][name]
    if list(fresh.poi_ids)!=saved['poi_ids'] or fresh.is_valid!=saved['is_valid']:issues.append([u['utterance_id'],name,'route_decision_mismatch'])
result={**counts,'issues':issues,'scope':'main run only; candidate equality and route node/validity equality, not bitwise equality of all artifacts'}
(Path(__file__).parent/'raw_trace_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
