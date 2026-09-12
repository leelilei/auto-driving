"""Fixed-rule development sample; no rejection sampling and no model calls."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.prepare_scene_pilot12 import COMMON, node, solve
from scripts.prepare_scene_rule30 import CHOICES, TEXT
from scripts.scene_pilot12 import write, digest, now
from src.scene_policy import Policy, execute

SEED = 20260911
SCENARIOS = ('open', 'departure', 'deadline', 'closing', 'combined')


def build_cases():
    rng = random.Random(SEED)
    cases = []
    for scenario in SCENARIOS:
        for draw in range(2):
            for selection in CHOICES:
                i = len(cases) + 1
                scene = dict(home=[0, 0], departure=540, speed_units_per_minute=1,
                    bank=node(rng.randint(8, 20), rng.randint(-4, 4), 500, 660),
                    bank_service=20, pharmacy_service=10, pharmacies={})
                ratings = rng.sample(range(20, 50), 5)
                for k in range(5):
                    opening = rng.choice((500, 535, 555, 575)) if scenario in ('departure', 'combined') else 500
                    closing = rng.choice((585, 595, 610, 660)) if scenario in ('closing', 'combined') else 660
                    scene['pharmacies'][f'P_{chr(65+k)}'] = node(rng.randint(-5, 25), rng.randint(-10, 10), opening, closing, ratings[k]/10)
                availability = 'departure' if scenario in ('departure', 'combined') else 'arrival'
                deadline = rng.choice((595, 605, 620)) if scenario in ('deadline', 'combined') else None
                extra = (' Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.'
                    if availability == 'departure' else ' Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.')
                if deadline is not None:
                    extra += f' Return home no later than {deadline//60:02d}:{deadline%60:02d}.'
                cases.append(dict(case_id=f'F{i:02d}', block_id=f'G{i:02d}', block_kind=scenario,
                    instruction=COMMON+TEXT[selection]+extra, scene=scene,
                    author_policy=dict(selection=selection, availability_reference=availability, return_by=deadline),
                    human_review_status='PENDING', provenance='Fixed-seed generated development case; no model-based filtering; no independent human label yet.'))
    return cases


def prepare(out):
    if out.exists():
        raise ValueError('Refuse overwrite; use a fresh directory')
    cases = build_cases()
    gold = []
    mutations = []
    for c in cases:
        result = solve(c['scene'], c['author_policy'])
        actual = execute(c['scene'], Policy.parse(c['author_policy']))
        assert actual == dict(status=result['status'], selected_poi_ids=sorted(result['accepted_poi_ids']))
        gold.append(dict(case_id=c['case_id'], policy=c['author_policy'], **result))
        for field, alternatives in [('selection', CHOICES), ('availability_reference', ('arrival', 'departure')), ('return_by', (None, 595, 605, 620))]:
            for value in alternatives:
                if value == c['author_policy'][field]:
                    continue
                mutant = solve(c['scene'], dict(c['author_policy'], **{field: value}))
                mutations.append(dict(case_id=c['case_id'], field=field, value=value,
                    changed=(mutant['status'], sorted(mutant['accepted_poi_ids'])) != (result['status'], sorted(result['accepted_poi_ids']))))
    out.mkdir(parents=True)
    write(out/'author_review_cases.json', cases)
    write(out/'model_inputs.json', [{k:c[k] for k in ('case_id', 'instruction', 'scene')} for c in cases])
    write(out/'gold_and_traces.json', gold)
    write(out/'mutation_audit.json', mutations)
    write(out/'run_plan.json', [dict(call_id=f"{c['case_id']}__r{rep}__{role}", case_id=c['case_id'], rep=rep, role=role)
        for rep in (1, 2) for c in cases for role in ('direct', 'language', 'evidence')])
    report = dict(status='PASS_ARITHMETIC_ONLY', human_review='PENDING', model_api_calls=0,
        seed=SEED, cases=30, independent_geometry_draws=30, pharmacies_per_case=5,
        scenarios=dict(Counter(c['block_kind'] for c in cases)), selections=dict(Counter(c['author_policy']['selection'] for c in cases)),
        feasible=sum(g['status']=='OK' for g in gold), infeasible=sum(g['status']=='INFEASIBLE' for g in gold),
        unique_solutions=sum(len(g['accepted_poi_ids'])==1 for g in gold),
        mutations=len(mutations), mutations_changing_decision=sum(m['changed'] for m in mutations),
        sampling='One deterministic pass, retain all draws including easy/infeasible/tied cases; no rejection or winner balancing.',
        limitation='Synthetic development sample using existing instruction templates; neither external benchmark nor evidence of a method gain.')
    write(out/'offline_validation.json', report)
    lines = ['# Fair30：30 个新案例语义审阅', '', '所有案例 PENDING。参考答案来自程序计算，未声称人工手算或人审通过。',
        '请核对：原句是否唯一表达作者规则；时间含义是否一致；表中计算是否遵守原句；有问题逐例记录。', '']
    for c, g in zip(cases, gold):
        lines += [f"## {c['case_id']} · {c['block_kind']}", '', c['instruction'], '',
            '作者待审规则：`'+json.dumps(c['author_policy'])+'`',
            f"场景：家(0,0)，银行({c['scene']['bank']['x']},{c['scene']['bank']['y']})；09:00出发；银行20分钟、药房10分钟；速度1。",
            '参考计算：`'+json.dumps(dict(status=g['status'], accepted=g['accepted_poi_ids']))+'`', '',
            '| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |',
            '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
        for row in g['candidates']:
            n = c['scene']['pharmacies'][row['poi_id']]
            lines.append(f"| {row['poi_id']} | ({n['x']},{n['y']}) | {n['open']}/{n['close']} | {n['rating']} | {row['distance_from_bank']:.3f} | {row['added_distance']:.3f} | {row['arrival']:.3f} | {row['service_finish']:.3f} | {row['return_time']:.3f} | {', '.join(row['reasons']) or '无'} |")
        lines += ['', '裁决：PENDING；问题：____；审核者/时间：____', '']
    (out/'CASE_REVIEW.md').write_text('\n'.join(lines)+'\n')
    write(out/'manifest.json', dict(created=now(), human_review='PENDING', model_api_calls=0,
        source_sha256=digest(Path(__file__)), files={p.name:digest(p) for p in out.iterdir() if p.is_file()}))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, default=ROOT/'data/scene_fair30_candidate')
    print(prepare(p.parse_args().out))
