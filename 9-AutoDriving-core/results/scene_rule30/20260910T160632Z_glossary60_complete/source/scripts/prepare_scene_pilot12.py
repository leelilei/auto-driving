"""Offline authoring and independent arithmetic checks; no model API calls."""
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/scene_pilot12_candidate'
COMMON=('Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. '
        'Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. '
        'Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. '
        'If no pharmacy can satisfy every requirement, report INFEASIBLE. ')

def node(x,y,opening=480,closing=1080,rating=4):
    return dict(x=x,y=y,open=opening,close=closing,rating=rating)

def world(a,b):
    return dict(home=[0,0],departure=540,speed_units_per_minute=1,bank=node(10,0),bank_service=20,
                pharmacy_service=10,pharmacies={'P_alpha':a,'P_beta':b})

def solve(scene,policy):
    home=scene['home'];bank=scene['bank'];bp=[bank['x'],bank['y']]
    bd=math.dist(home,bp);ba=scene['departure']+bd;bf=ba+scene['bank_service'];rows=[]
    for pid,p in scene['pharmacies'].items():
        pos=[p['x'],p['y']];dist=math.dist(bp,pos);arr=bf+dist;finish=arr+scene['pharmacy_service'];ret=finish+math.dist(pos,home)
        reasons=[]
        if ba<bank['open'] or bf>bank['close']:reasons.append('bank_service_window')
        if arr<p['open']:reasons.append('pharmacy_not_open_on_arrival')
        if finish>p['close']:reasons.append('pharmacy_service_finishes_after_close')
        if policy['availability_reference']=='departure' and not p['open']<=scene['departure']<p['close']:reasons.append('not_open_at_departure')
        if policy['return_by'] is not None and ret>policy['return_by']:reasons.append('return_deadline')
        detour=dist+math.dist(pos,home)-math.dist(bp,home)
        objective={'nearest_from_bank':dist,'minimum_added_distance':detour,'highest_rating':-p['rating']}[policy['selection']]
        rows.append(dict(poi_id=pid,arrival=arr,service_finish=finish,return_time=ret,distance_from_bank=dist,
                         added_distance=detour,rating=p['rating'],feasible=not reasons,reasons=reasons,objective=objective))
    feasible=[r for r in rows if r['feasible']]
    best=min((r['objective'] for r in feasible),default=None)
    accepted=[r['poi_id'] for r in feasible if math.isclose(r['objective'],best,rel_tol=0,abs_tol=1e-9)]
    return dict(status='OK' if accepted else 'INFEASIBLE',accepted_poi_ids=accepted,candidates=rows)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cases=[]
    def add(cid,pair,kind,instruction,scene,selection,expected,availability='arrival',deadline=None):
        policy=dict(selection=selection,availability_reference=availability,return_by=deadline)
        cases.append(dict(case_id=cid,pair_id=pair,pair_kind=kind,instruction=COMMON+instruction,scene=scene,
                          author_policy=policy,hand_expected=expected,human_review_status='PENDING',provenance='author_constructed_development_only'))
    w=world(node(15,0,closing=580),node(22,0,closing=620))
    text='Among pharmacies where service can be completed during opening hours, choose the one closest to bank B.'
    add('S01','F1','scene_change',text,w,'nearest_from_bank',['P_beta'])
    w=copy.deepcopy(w);w['pharmacies']['P_alpha']['close']=600
    add('S02','F1','scene_change',text,w,'nearest_from_bank',['P_alpha'])
    w=world(node(11,0,rating=4),node(15,0,rating=4.9))
    add('S03','F2','instruction_change','Choose the highest-rated feasible pharmacy and return home by 09:55.',w,'highest_rating',['P_alpha'],deadline=595)
    add('S04','F2','instruction_change','Choose the highest-rated feasible pharmacy and return home by 10:05.',copy.deepcopy(w),'highest_rating',['P_beta'],deadline=605)
    w=world(node(10,2),node(5,0))
    text='Choose the feasible pharmacy that adds the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).'
    add('S05','F3','scene_change',text,w,'minimum_added_distance',['P_beta'])
    w=copy.deepcopy(w);w['pharmacies']['P_beta']['y']=5
    add('S06','F3','scene_change',text,w,'minimum_added_distance',['P_alpha'])
    w=world(node(12,0,closing=581,rating=4.9),node(8,0,closing=600,rating=4))
    text='Choose the highest-rated pharmacy among those whose full service can finish by closing time.'
    add('S07','F4','scene_change',text,w,'highest_rating',['P_beta'])
    w=copy.deepcopy(w);w['pharmacies']['P_alpha']['close']=582
    add('S08','F4','scene_change',text,w,'highest_rating',['P_alpha'])
    w=world(node(11,0,opening=565,closing=600),node(15,0,opening=500,closing=650))
    add('S09','F5','instruction_change','Restrict the choice to pharmacies already open when I leave home at 09:00. Among those that can also complete service when visited, choose the one closest to bank B.',w,'nearest_from_bank',['P_beta'],availability='departure')
    add('S10','F5','instruction_change','A pharmacy need not be open at 09:00; it must be open when I reach it after the bank visit and allow the full service. Choose the one closest to bank B.',copy.deepcopy(w),'nearest_from_bank',['P_alpha'])
    w=world(node(11,0,rating=4),node(15,0,rating=4.9))
    text='Choose the feasible pharmacy closest to bank B and return home by 09:10.'
    add('S11','F6','irrelevant_scene_change',text,w,'nearest_from_bank',[],deadline=550)
    w=copy.deepcopy(w);w['pharmacies']['P_beta']['rating']=1
    add('S12','F6','irrelevant_scene_change',text,w,'nearest_from_bank',[],deadline=550)
    gold=[]
    for c in cases:
        result=solve(c['scene'],c['author_policy'])
        assert result['accepted_poi_ids']==c['hand_expected'],c['case_id']
        # Independently hand-specified expectations, not selected from model results.
        gold.append(dict(case_id=c['case_id'],policy=c['author_policy'],hand_expected=c['hand_expected'],**result))
    assert len(cases)==12 and len(gold)==12
    assert all(len(g['accepted_poi_ids'])==1 for g in gold[:10])
    assert all(g['status']=='INFEASIBLE' for g in gold[10:])
    # Exact arithmetic anchors check arrival/service/return definitions.
    assert gold[0]['candidates'][0]['arrival']==575 and gold[0]['candidates'][0]['service_finish']==585
    assert gold[2]['candidates'][0]['return_time']==592 and gold[2]['candidates'][1]['return_time']==600
    assert gold[7]['candidates'][0]['service_finish']==582
    public=[{k:c[k] for k in ('case_id','instruction','scene')} for c in cases]
    def dump(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    dump('model_inputs.json',public);dump('author_review_cases.json',cases);dump('gold_and_traces.json',gold)
    dump('offline_validation.json',dict(status='PASS_OFFLINE_ARITHMETIC_ONLY',cases=12,feasible_unique=10,infeasible=2,
                pairs=6,changed_answer_pairs=5,invariant_pairs=1,model_api_calls=0,human_review='PENDING',
                note='Reference calculations and hand expectations agree; not a full production solver or independent human audit.'))
    manifest=dict(stage='CANDIDATE_NOT_ADMITTED',model_api_calls=0,human_review='PENDING',files={})
    for name in ['model_inputs.json','author_review_cases.json','gold_and_traces.json','offline_validation.json']:
        manifest['files'][name]=hashlib.sha256((OUT/name).read_bytes()).hexdigest()
    dump('candidate_manifest.json',manifest)
    print(json.dumps(json.loads((OUT/'offline_validation.json').read_text()),indent=2))

if __name__=='__main__':main()
