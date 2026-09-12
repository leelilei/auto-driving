"""Export supplemental tables from the verified frozen results; no new evaluation/API."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = ROOT / '9-AutoDriving-core/results/v4_1/closeout_v2c_20260912'
OUT = Path(__file__).parent

def read(name):
    return json.loads((BUNDLE / name).read_text())

def export(name, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

joint = read('joint_metrics.json')
export('joint_metrics.csv', [dict(model=model, method=method, **{
    k: json.dumps(v) if isinstance(v, list) else v for k, v in values.items()
}) for model, data in joint.items() for method, values in data['methods'].items()])

records, selections = read('evaluated_records.json'), read('selections.json')
penalties = []
for model, items in records.items():
    for method, ids in selections[model].items():
        selected = set(ids)
        outcomes = [x['outcomes'][int(x['uid'] in selected)] for x in items]
        for penalty in [0.01, 0.1, 1.0]:
            penalties.append(dict(model=model, method=method, failure_penalty=penalty,
                n=len(items), failures=sum(not o['success'] for o in outcomes),
                loss=sum(o['loss'] if o['success'] else penalty for o in outcomes)/len(items)))
export('failure_penalty_sensitivity.csv', penalties)
print('Exported joint_metrics.csv and failure_penalty_sensitivity.csv')
