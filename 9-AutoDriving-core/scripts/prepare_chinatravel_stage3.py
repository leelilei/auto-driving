"""Freeze public inputs for the six-case ChinaTravel interface pilot."""
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'9-AutoDriving-core/data/chinatravel_dev_60.json'
SEL=ROOT/'docs/experiments/chinatravel_setup/semantic_audit_20260911/results/selected_dev10.json'
OUT=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'
def main():
    if OUT.exists(): raise RuntimeError('refuse overwrite')
    data=json.loads(DATA.read_text()); selected=json.loads(SEL.read_text())['cases'][:6]
    rows=[{'uid':x['uid'],'nature_language':data[x['uid']]['nature_language']} for x in selected]
    OUT.mkdir(parents=True); (OUT/'public_inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    protocol={'stage':'STAGE3_OFFLINE_READY_NOT_COLLECTED','model_api_calls':0,'n_cases':6,'ids':[x['uid'] for x in selected], 'gold_in_inputs':False,'source':'fixed selected_dev10 first six; no outcome-based selection'}
    (OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
    manifest={'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir()},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(protocol,ensure_ascii=False))
if __name__=='__main__': main()
