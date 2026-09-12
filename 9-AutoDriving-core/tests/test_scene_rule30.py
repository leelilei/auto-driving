"""Structural and metamorphic checks for the prospective supplement."""
from copy import deepcopy
import json
import pytest
from scripts.prepare_scene_rule30 import build_cases,audit,CHOICES,IDS
from src.scene_policy import Policy,execute,request

@pytest.fixture(scope='module')
def cases():return build_cases()

def test_design_covers_all_objectives_and_retains_insensitive_controls(cases):
    gold,mutations,report=audit(cases)
    assert report['primary_wrong_objective_decisions_changed']=='36/36'
    assert report['unique_feasible']==28 and report['infeasible']==2
    assert len(mutations)==240
    assert any(not m['changed_decision'] for m in mutations)
    assert all(c['human_review_status']=='PENDING' for c in cases)
    assert len({c['case_id'] for c in cases})==30

@pytest.mark.parametrize('index',range(18))
def test_rotation_and_id_renaming_preserve_physical_choice(cases,index):
    c=cases[index];scene=deepcopy(c['scene']);p=Policy.parse(c['author_policy'])
    original=execute(scene,p)['selected_poi_ids']
    names=dict(zip(IDS,('renamed_z','renamed_x','renamed_y')))
    for n in [scene['bank'],*scene['pharmacies'].values()]:n['x'],n['y']=-n['y'],n['x']
    scene['home']=[-scene['home'][1],scene['home'][0]]
    scene['pharmacies']={names[k]:v for k,v in reversed(list(scene['pharmacies'].items()))}
    assert execute(scene,p)['selected_poi_ids']==sorted(names[k] for k in original)

def test_pairs_change_only_the_declared_factor(cases):
    by_id={c['case_id']:c for c in cases}
    for left,right in [('R19','R20'),('R21','R22')]:
        a,b=by_id[left],by_id[right]
        assert a['scene']==b['scene']
        assert a['hand_expected']!=b['hand_expected']
    a,b=by_id['R23'],by_id['R24']
    assert a['instruction']==b['instruction'] and a['author_policy']==b['author_policy']
    changed=deepcopy(a['scene']);changed['pharmacies']['P_alpha']['close']=582
    assert changed==b['scene']
    for left,right in [('R25','R26'),('R29','R30')]:
        a,b=by_id[left],by_id[right]
        assert a['instruction']==b['instruction'] and a['author_policy']==b['author_policy']
        assert a['hand_expected']==b['hand_expected']
        assert a['scene']!=b['scene']

def test_label_permutation_preserves_selected_location(cases):
    a,b=cases[26:28]
    assert a['instruction']==b['instruction'] and a['author_policy']==b['author_policy']
    assert a['hand_expected']!=b['hand_expected']
    assert a['scene']['pharmacies'][a['hand_expected'][0]]==b['scene']['pharmacies'][b['hand_expected'][0]]

def test_all_methods_receive_same_public_scene_without_author_metadata(cases):
    for c in cases:
        policy=Policy.parse(c['author_policy'])
        users=[json.loads(request(c,role,policy if role!='direct' else None)['user']) for role in ('direct','language','evidence')]
        assert all(u['scene']==c['scene'] and u['instruction']==c['instruction'] for u in users)
        assert all(not set(u)&{'author_policy','hand_expected','block_id','block_kind','case_id','human_review_status'} for u in users)

def test_complete_triplets_balance_poi_ids(cases):
    for selection in CHOICES:
        winners=[c['hand_expected'][0] for c in cases[:18] if c['author_policy']['selection']==selection]
        assert all(winners.count(pid)==2 for pid in IDS)
