"""Stage-3 gate: verify fixed six inputs before any model collection."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'

def main():
    public=json.loads((RUN/'public_inputs.json').read_text())
    assert len(public)==6 and all(set(x)=={'uid','nature_language'} for x in public)
    protocol=json.loads((RUN/'protocol.json').read_text())
    assert protocol['model_api_calls']==0 and protocol['gold_in_inputs'] is False
    report={'status':'GATED_NOT_COLLECTED','n_cases':len(public),'model_api_calls':0,
            'reason':'Existing collector is single-regression hard-coded; batch collector must be implemented before calls.',
            'ids':[x['uid'] for x in public], 'failure_classes':['parse_error','unsupported_requirement','compile_error','search_failure','data_coverage_failure','evaluation_mismatch','semantic_error']}
    (RUN/'stage3_gate.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
