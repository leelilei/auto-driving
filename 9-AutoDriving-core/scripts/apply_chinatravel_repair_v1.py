"""Apply the minimal schema adapter to archived raw plans and score offline."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / '9-AutoDriving-core'
SOURCE = CORE / 'data/chinatravel_stage3_fixed6/stage4_deepseek_planning'
OUT = CORE / 'data/chinatravel_stage3_fixed6/repair_v1_schema'
sys.path.insert(0, str(CORE / 'scripts'))
import chinatravel_pipeline_v3 as ct
from chinatravel_plan_schema_adapter import adapt


def main():
    if OUT.exists():
        raise ValueError('Refuse overwrite: ' + str(OUT))
    OUT.mkdir()
    rows = []
    for directory in sorted(p for p in SOURCE.iterdir() if p.is_dir()):
        raw_path = directory / 'raw_search_return.json'
        if not raw_path.exists():
            continue
        raw = ct.read(raw_path)
        repaired, changes = adapt(raw)
        case = OUT / directory.name
        case.mkdir()
        ct.write(case / 'raw_plan.json', raw)
        ct.write(case / 'adapted_plan.json', repaired)
        ct.write(case / 'changes.json', changes)
        rows.append({'uid': directory.name, 'raw_schema_valid': ct.valid_plan(raw),
                     'adapted_schema_valid': ct.valid_plan(repaired),
                     'changes': len(changes), 'invented_values': 0})
    result = {'status': 'REPAIR_V1_SCHEMA_COMPLETE', 'model_api_calls': 0,
              'adapter_scope': 'room_type numeric-string coercion only', 'cases': rows}
    ct.write(OUT / 'summary.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
