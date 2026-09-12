"""Bounded Stage-3 collector; refuses to call without explicit API credentials."""
import json, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'
def main():
    public=json.loads((RUN/'public_inputs.json').read_text())
    if not (os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')):
        report={'status':'BLOCKED_NO_API_CREDENTIALS','model_api_calls':0,'n_cases':len(public),
                'ids':[x['uid'] for x in public], 'max_requests':len(public),
                'reason':'No API credential in environment; no network call attempted.'}
        (RUN/'collection_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False)); return
    raise RuntimeError('Credentials present: invoke reviewed collector implementation, not this safety stub.')
if __name__=='__main__': main()
