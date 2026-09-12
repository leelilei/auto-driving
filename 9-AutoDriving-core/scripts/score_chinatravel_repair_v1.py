"""Score Repair v1 plans against canonical official queries, offline."""
import contextlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / '9-AutoDriving-core'
OUT = CORE / 'data/chinatravel_stage3_fixed6/repair_v1_schema'
UPSTREAM = ROOT / 'external/ChinaTravel/chinatravel/data/dev_split'
sys.path.insert(0, str(CORE / 'scripts'))
import chinatravel_pipeline_v3 as ct


def main():
    rows = []
    for directory in sorted(p for p in OUT.iterdir() if p.is_dir()):
        uid = directory.name
        plan = ct.read(directory / 'adapted_plan.json')
        query = ct.read(UPSTREAM / f'{uid}.json')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            score = ct.json_safe(ct.v1.evaluate({uid: query}, {uid: plan}))
        ct.write(directory / 'official_score.json', score)
        rows.append({'uid': uid, 'schema_rate': score['schema_rate'],
                     'commonsense_macro': score['commonsense_macro'],
                     'hard_macro': score['hard_macro'],
                     'all_pass_rate': score['all_pass_rate']})
    result = {'status': 'REPAIR_V1_OFFICIAL_SCORE_COMPLETE',
              'model_api_calls': 0, 'cases': rows}
    ct.write(OUT / 'official_summary.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
