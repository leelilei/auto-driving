"""Prospective, authored rule-discrimination supplement. Offline only."""
import argparse
from copy import deepcopy
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.prepare_scene_pilot12 import COMMON,node,solve
from src.scene_policy import Policy,execute,request

CHOICES=('nearest_from_bank','minimum_added_distance','highest_rating')
IDS=('P_alpha','P_beta','P_gamma')
# Six fixed geometries, not searched against any model response or score.
GEOMETRIES=(
    ((10,2),(4,0),(15,6)),
    ((11,1),(6,0),(6,6)),
    ((9,2),(2,0),(13,-4)),
    ((12,1),(7,0),(0,5)),
    ((8,-1),(3,0),(12,-6)),
    ((10,-3),(5,1),(16,2)),
)
TEXT={
 'nearest_from_bank':'Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.',
 'minimum_added_distance':'Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).',
 'highest_rating':'Among pharmacies satisfying every requirement, choose the one with the highest rating.',
}
DEADLINES=(None,550,590,595,600,630)

def layout(i):
    scene=dict(home=[0,0],departure=540,speed_units_per_minute=1,bank=node(10,0,500,660),
               bank_service=20,pharmacy_service=10,pharmacies={})
    winners={}
    for j,(selection,xy,rating) in enumerate(zip(CHOICES,GEOMETRIES[i],(4,3.5,4.9))):
        pid=IDS[(i+j)%3];scene['pharmacies'][pid]=node(*xy,500,660,rating)
        winners[selection]=pid
    # Presentation order never reveals the objective role.
    scene['pharmacies']=dict(sorted(scene['pharmacies'].items()))
    return scene,winners

def build_cases():
    cases=[]
    def add(cid,block,kind,scene,selection,expected,availability='arrival',deadline=None,extra=''):
        cases.append(dict(case_id=cid,block_id=block,block_kind=kind,
            instruction=COMMON+TEXT[selection]+extra,scene=deepcopy(scene),
            author_policy=dict(selection=selection,availability_reference=availability,return_by=deadline),
            hand_expected=expected,human_review_status='PENDING',
            provenance='Authored after Scene-Pilot12 analysis; prospective development supplement, not independent confirmatory data.'))
    for i in range(6):
        scene,winners=layout(i)
        for j,selection in enumerate(CHOICES):
            add(f'R{i*3+j+1:02d}',f'G{i+1}','objective_triple',scene,selection,[winners[selection]])
    # Eligibility reference: near pharmacy opens after departure but before arrival.
    scene,w=layout(0);scene['pharmacies'][w['nearest_from_bank']]['open']=565
    add('R19','C1','availability_pair',scene,'nearest_from_bank',['P_beta'],availability='departure',
        extra=' Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.')
    add('R20','C1','availability_pair',scene,'nearest_from_bank',['P_alpha'],
        extra=' Pharmacies need not be open when I leave home at 09:00; they must be open when I arrive and allow the full service.')
    # Return deadline, including an exact equality boundary at 600 minutes.
    scene,_=layout(0)
    scene['pharmacies']={IDS[0]:node(11,0,500,660,4),IDS[1]:node(8,0,500,660,3.5),IDS[2]:node(15,0,500,660,4.9)}
    add('R21','C2','deadline_pair',scene,'highest_rating',['P_alpha'],deadline=595,extra=' Return home no later than 09:55.')
    add('R22','C2','deadline_pair',scene,'highest_rating',['P_gamma'],deadline=600,extra=' Return home no later than 10:00.')
    # Service completion, not merely arrival, determines feasibility.
    scene['pharmacies']={IDS[0]:node(12,0,500,581,4.9),IDS[1]:node(8,0,500,660,4),IDS[2]:node(15,0,500,660,3.5)}
    add('R23','C3','closing_pair',scene,'highest_rating',['P_beta'])
    scene=deepcopy(scene);scene['pharmacies']['P_alpha']['close']=582
    add('R24','C3','closing_pair',scene,'highest_rating',['P_alpha'])
    # Rating change cannot affect a pure nearest objective.
    scene,w=layout(1)
    add('R25','C4','irrelevant_rating_pair',scene,'nearest_from_bank',[w['nearest_from_bank']])
    scene=deepcopy(scene);scene['pharmacies'][w['nearest_from_bank']]['rating']=0.5
    add('R26','C4','irrelevant_rating_pair',scene,'nearest_from_bank',[w['nearest_from_bank']])
    # Rename IDs only; physical selection must remain identical.
    scene,w=layout(4)
    add('R27','C5','id_permutation_pair',scene,'minimum_added_distance',[w['minimum_added_distance']])
    rename=dict(zip(IDS,('P_beta','P_gamma','P_alpha')))
    scene=deepcopy(scene);scene['pharmacies']=dict(sorted((rename[k],v) for k,v in scene['pharmacies'].items()))
    add('R28','C5','id_permutation_pair',scene,'minimum_added_distance',[rename[w['minimum_added_distance']]])
    # Impossible deadline remains impossible even if ratings change.
    scene,w=layout(2)
    add('R29','C6','infeasible_invariance_pair',scene,'highest_rating',[],deadline=550,extra=' Return home no later than 09:10.')
    scene=deepcopy(scene);scene['pharmacies'][w['highest_rating']]['rating']=1
    add('R30','C6','infeasible_invariance_pair',scene,'highest_rating',[],deadline=550,extra=' Return home no later than 09:10.')
    return cases

def decision(result):return (result['status'],tuple(sorted(result['accepted_poi_ids'])))

def audit(cases):
    gold=[];mutations=[]
    for c in cases:
        p=c['author_policy'];ref=solve(c['scene'],p)
        assert ref['accepted_poi_ids']==c['hand_expected'],c['case_id']
        actual=execute(c['scene'],Policy.parse(p))
        assert (actual['status'],tuple(actual['selected_poi_ids']))==decision(ref)
        gold.append(dict(case_id=c['case_id'],policy=p,**ref))
        for field,alternatives in [('selection',CHOICES),('availability_reference',('arrival','departure')),('return_by',DEADLINES)]:
            for alt in alternatives:
                if alt==p[field]:continue
                wrong=dict(p);wrong[field]=alt;out=solve(c['scene'],wrong)
                mutations.append(dict(case_id=c['case_id'],block_id=c['block_id'],field=field,
                     alternate_value=alt,changed_decision=decision(out)!=decision(ref),
                     mutant_status=out['status'],mutant_poi_ids=out['accepted_poi_ids']))
        # Whitelist metadata away from the actual inference request.
        exposed=json.loads(request(c,'direct')['user'])
        assert set(exposed)=={'instruction','scene'}
    primary=[m for m in mutations if m['case_id'] in {c['case_id'] for c in cases[:18]} and m['field']=='selection']
    assert len(primary)==36 and all(m['changed_decision'] for m in primary)
    for i in range(6):
        triple=cases[i*3:i*3+3]
        assert all(c['scene']==triple[0]['scene'] for c in triple)
        assert {c['hand_expected'][0] for c in triple}==set(IDS)
    counts={selection:dict(Counter(c['hand_expected'][0] for c in cases[:18] if c['author_policy']['selection']==selection)) for selection in CHOICES}
    assert all(set(v.values())=={2} and set(v)==set(IDS) for v in counts.values())
    old=json.loads((ROOT/'data/scene_pilot12_candidate/author_review_cases.json').read_text())
    old_nearest=[c for c in old if c['author_policy']['selection']=='nearest_from_bank']
    old_changes=sum(decision(solve(c['scene'],c['author_policy']))!=decision(solve(c['scene'],dict(c['author_policy'],selection='minimum_added_distance'))) for c in old_nearest)
    report=dict(status='PASS_OFFLINE_DISCRIMINATION_ONLY',cases=30,primary_cases=18,control_cases=12,
        unique_feasible=sum(g['status']=='OK' and len(g['accepted_poi_ids'])==1 for g in gold),
        infeasible=sum(g['status']=='INFEASIBLE' for g in gold),
        primary_wrong_objective_decisions_changed='36/36',balanced_primary_winners=counts,
        mutation_audit_count=len(mutations),mutation_decisions_changed=sum(m['changed_decision'] for m in mutations),
        old_nearest_to_added_distance=dict(cases=len(old_nearest),changed_decisions=old_changes),
        model_api_calls=0,human_review='PENDING',
        caveat='Mutation discrimination is an offline dataset property, not model accuracy or DARC improvement. Six primary geometries and control reuses are clustered, not thirty independent samples.')
    return gold,mutations,report

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'data/scene_rule30_candidate');args=p.parse_args()
    if args.out.exists():raise ValueError('Refuse overwrite; use a fresh version directory')
    cases=build_cases();gold,mutations,report=audit(cases)
    args.out.mkdir(parents=True)
    def save(name,value):(args.out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    save('model_inputs.json',[{k:c[k] for k in ('case_id','instruction','scene')} for c in cases])
    save('author_review_cases.json',cases);save('gold_and_traces.json',gold)
    save('mutation_audit.json',mutations);save('offline_validation.json',report)
    save('run_plan.json',[dict(call_id=f"{c['case_id']}__r{rep}__{role}",case_id=c['case_id'],rep=rep,role=role)
                        for rep in (1,2) for c in cases for role in ('direct','language','evidence')])
    lines=['# Scene-Rule30 候选案例审阅表','',
           '状态：PENDING。仅离线作者计算，尚未模型调用。审核应核对原句、规则、场景时刻与预期，而非只认可计算结果。',
           '这是根据既有开发诊断补充的数据，不是未暴露的确认性测试集。','']
    for c,g in zip(cases,gold):
        lines += [f"## {c['case_id']} · {c['block_id']} · {c['block_kind']}",'',c['instruction'],'',
                  '作者规则：`'+json.dumps(c['author_policy'],ensure_ascii=False)+'`',
                  '手定预期：`'+json.dumps(c['hand_expected'])+'`；参考状态：'+g['status'],'',
                  '| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |',
                  '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
        for r in g['candidates']:
            n=c['scene']['pharmacies'][r['poi_id']]
            lines.append(f"| {r['poi_id']} | ({n['x']}, {n['y']}) | {n['open']}–{n['close']} | {n['rating']} | {r['distance_from_bank']:.3f} | {r['added_distance']:.3f} | {r['arrival']:.3f} | {r['service_finish']:.3f} | {r['return_time']:.3f} | {r['feasible']} |")
        lines+=['','审核者：____；时间：____；裁决：PENDING；问题/修订：____','']
    (args.out/'CASE_REVIEW.md').write_text('\n'.join(lines)+'\n')
    save('manifest.json',dict(created=datetime.now(timezone.utc).isoformat(),scope='PROSPECTIVE_DEVELOPMENT_SUPPLEMENT',
        human_review='PENDING',model_api_calls=0,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in args.out.iterdir() if f.is_file()}))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
