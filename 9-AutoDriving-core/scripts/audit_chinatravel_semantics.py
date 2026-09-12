"""Source-grounded audit of the frozen 60 dev queries; no model/network/solver calls.

Dataset-specific source review, NOT a production semantic parser or new gold.
Human-query annotations below were reviewed against each complete original text.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
CORE=ROOT/'9-AutoDriving-core'
UPSTREAM=ROOT/'external/ChinaTravel'
DATA=CORE/'data/chinatravel_dev_60.json'
ANNOTATIONS=ROOT/'docs/experiments/chinatravel_setup/semantic_audit_20260911/review_annotations.json'
NUM={'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7}
FUNCTIONS={'days':'day_count','people_number':'people_count','budget':'activity_cost',
    'room_count':'room_count','room_type':'room_type','cuisine':'restaurant_type',
    'attraction_category':'attraction_type','poi_names':'activity_position',
    'intercity_mode':'intercity_transport_type','innercity_mode':'innercity_transport_type',
    'child_friendly_attractions':'attraction_type','duration_prose':'day_count'}


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def number(text):return int(text) if text.isdigit() else NUM[text]


def calls(code):
    return {node.func.id for node in ast.walk(ast.parse(code)) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)}


def dsl_indices(query,field):
    indices=[]
    for i,code in enumerate(query['hard_logic_py']):
        names=calls(code)
        if field=='budget':
            match='activity_cost' in names and 'innercity_transport_cost' in names
        elif field=='hotel_nightly_budget':
            match='activity_cost' in names and 'room_count' not in names and 'innercity_transport_cost' not in names
        elif field=='innercity_mode':
            match='innercity_transport_type' in names and 'taxi_cars' not in names and 'metro_tickets' not in names
        else:match=FUNCTIONS.get(field) in names
        if match:indices.append(i)
    return indices


def requirement(query,field,quote,value=None,coverage=None,note='',modality='explicit'):
    if not quote or quote not in query['nature_language']:raise ValueError('Ungrounded annotation: '+query['uid']+' '+quote)
    indices=dsl_indices(query,field)
    if coverage is None:coverage='direct' if indices else 'absent'
    if field in ('start_city','target_city'):
        coverage='commonsense_route_binding'
    return {'field':field,'quote':quote,'value':value,'modality':modality,
            'official_coverage':coverage,'dsl_indices':indices,'note':note,
            'current_interface_support':field in ('start_city','target_city','days','people_number','budget')}


def inspect_query(query,annotation):
    text=query['nature_language'];tag=query['tag'];requirements=[]
    if tag=='human':
        match=re.match(r'\[当前位置([^,]+),目标位置([^,]+),旅行人数(\d+),旅行天数(\d+)\]',text)
        if not match:raise ValueError('Unreviewed human header')
        values={'start_city':match[1],'target_city':match[2],'people_number':int(match[3]),'days':int(match[4])}
        quotes={'start_city':'当前位置'+match[1],'target_city':'目标位置'+match[2],
                'people_number':'旅行人数'+match[3],'days':'旅行天数'+match[4]}
    else:
        match=re.search(r'当前位置([^。]+)。(.*?)去([^，。]+?)玩([一两二三四五六七\d]+)天',text)
        if not match:raise ValueError('Unreviewed generated template')
        who=match[2]
        if '我一个人' in who:people,quote=1,'我一个人'
        elif '我和两个朋友' in who:people,quote=3,'我和两个朋友'
        elif '我们' in who:
            person=re.search(r'我们([一两二三四\d]+)个人',who)
            if not person:raise ValueError('Unreviewed party expression')
            people,quote=number(person[1]),person[0]
        elif '我和' in who:
            person=re.search(r'我和(?:男朋友|女朋友|朋友)',who)
            if not person:raise ValueError('Unreviewed companion')
            people,quote=2,person[0]
        else:people,quote=1,'我'
        values={'start_city':match[1],'target_city':match[3],'days':number(match[4]),'people_number':people}
        quotes={'start_city':'当前位置'+match[1],'target_city':'去'+match[3],
                'days':'玩'+match[4]+'天','people_number':quote}
    for field,value in values.items():
        if value!=query[field]:raise ValueError('Text/base metadata disagreement: '+query['uid']+'/'+field)
        requirements.append(requirement(query,field,quotes[field],value))
    if tag!='human':
        budget=re.search(r'(?:总)?预算(\d+)(?:人民币|元)',text)
        if not budget:raise ValueError('Generated query missing budget')
        requirements.append(requirement(query,'budget',budget[0],int(budget[1])))
        room=re.search(r'开([一两二])间(单床房|双床房|房)',text)
        if room:
            requirements.append(requirement(query,'room_count',room[0],number(room[1])))
            if room[2]!='房':requirements.append(requirement(query,'room_type',room[2],{'单床房':1,'双床房':2}[room[2]]))
        cuisine=re.search(r'想吃([^，。]+)',text)
        if cuisine:requirements.append(requirement(query,'cuisine',cuisine[0],cuisine[1]))
        intercity=re.search(r'选择(火车|飞机)出行',text)
        if intercity:requirements.append(requirement(query,'intercity_mode',intercity[0],{'火车':'train','飞机':'airplane'}[intercity[1]]))
        innercity=re.search(r'市内(?:交通)?主要使用(地铁|出租车)',text)
        if innercity:requirements.append(requirement(query,'innercity_mode',innercity[0],{'地铁':'metro','出租车':'taxi'}[innercity[1]],
            'weaker_quantifier','DSL 只要求指定方式至少出现一次；没有次数、距离或时长占比，更没有最优性条件。','preference_unquantified'))
        for phrase,category in [('想欣赏历史古迹','历史古迹'),('想去商业街区购物','商业街区')]:
            if phrase in text:requirements.append(requirement(query,'attraction_category',phrase,category,
                note='编码至少一次该类景点；购物目的本身没有购买行为指标。' if category=='商业街区' else ''))
        hotel=re.search(r'希望酒店每晚不超过(\d+)元',text)
        if hotel:requirements.append(requirement(query,'hotel_nightly_budget',hotel[0],int(hotel[1]),
            'unit_scope_mismatch','原句未说人均；DSL 为全部酒店费用 / 人数 / 夜数，既人均化又跨夜平均。'))
    for item in annotation.get('requirements',[]):
        requirements.append(requirement(query,**item))
    conflicts=annotation.get('conflicts',[])
    for conflict in conflicts:
        for quote in conflict['quotes']:
            if quote not in text:raise ValueError('Ungrounded conflict evidence')
    unresolved=annotation.get('interpretation_notes',[])
    has_budget=any(r['field']=='budget' for r in requirements)
    gaps=sorted({r['field'] for r in requirements if not r['current_interface_support']})
    if not has_budget:gaps.append('optional_budget_null')
    if conflicts:gaps.append('source_conflict_preservation')
    issues=sorted({r['official_coverage'] for r in requirements if r['official_coverage'] not in ('direct','commonsense_route_binding')})
    if conflicts:issues.append('source_conflict')
    all_dsl=[{'index':i,'code':code,'functions':sorted(calls(code))} for i,code in enumerate(query['hard_logic_py'])]
    return {'uid':query['uid'],'tag':tag,'nature_language':text,'requirements':requirements,
        'budget_specified':has_budget,'current_interface_gaps':gaps,
        'current_interface_textually_complete':not gaps,
        'evaluation_issues':issues,'conflicts':conflicts,'interpretation_notes':unresolved,
        'official_constraints':all_dsl,'official_constraint_count':len(all_dsl),
        'family_signature':('easy_single_person_one_day_budget_template' if tag=='easy' else
            'generated:'+','.join(sorted({r['field'] for r in requirements})) if tag=='medium' else 'human:'+query['uid']),
        'family_note':'结构模板标识，仅用于暴露聚集性；不是独立意图或语义家族划分证明。',
        'review':'Codex source review; no independent human signoff; not new gold or a production parsing rule'}


STRATA=[('regression_base','已暴露回归例；现有五字段链路',lambda r:r['uid']=='e20241028160248698752','baseline'),
 ('food_rooms','餐饮类型＋房数/房型',lambda r:r['tag']=='medium' and any(x['field']=='cuisine' for x in r['requirements']),'interface_extension'),
 ('train_rooms','火车＋多人住宿',lambda r:r['tag']=='medium' and any(x['field']=='intercity_mode' and x['value']=='train' for x in r['requirements']),'interface_extension'),
 ('airplane_rooms','飞机＋住宿',lambda r:r['tag']=='medium' and any(x['field']=='intercity_mode' and x['value']=='airplane' for x in r['requirements']),'interface_extension'),
 ('attraction_category','明确景点类别',lambda r:r['tag']=='medium' and any(x['field']=='attraction_category' for x in r['requirements']),'interface_extension'),
 ('unspecified_budget','无预算、无额外偏好；不得虚构数值预算',lambda r:r['tag']=='human' and not r['budget_specified'] and all(x['field'] in ('start_city','target_city','days','people_number') for x in r['requirements']),'interface_extension'),
 ('majority_mode','主要交通方式的量词边界',lambda r:any(x['official_coverage']=='weaker_quantifier' for x in r['requirements']),'diagnostic_only'),
 ('hotel_budget_unit','酒店每晚预算的单位边界',lambda r:any(x['field']=='hotel_nightly_budget' for x in r['requirements']),'diagnostic_only'),
 ('omitted_explicit_budget','明确预算未进入 DSL',lambda r:any(x['field']=='budget' and x['official_coverage']=='absent' for x in r['requirements']),'diagnostic_only'),
 ('conflicting_duration','前缀/正文天数冲突',lambda r:bool(r['conflicts']),'diagnostic_only')]


def select(rows):
    selected=[];used=set()
    for key,reason,predicate,track in STRATA:
        candidates=sorted(r['uid'] for r in rows if predicate(r) and r['uid'] not in used)
        if not candidates:raise ValueError('Empty selection stratum: '+key)
        uid=candidates[0];used.add(uid)
        selected.append({'stratum':key,'uid':uid,'reason':reason,'track':track,
            'selection_candidates':candidates,'status':'not_executed',
            'prior_exposed_regression':key=='regression_base'})
    return selected


def run(out):
    raw=read(DATA);annotations=read(ANNOTATIONS)
    split=read(UPSTREAM/'dev_hold_split.json')['splits']
    dev={uid for part in split.values() for uid in part['dev_uids']}
    hold={uid for part in split.values() for uid in part['hold_uids']}
    if set(raw)!=dev or dev&hold or len(dev)!=60 or len(hold)!=544:raise ValueError('Frozen split mismatch')
    if set(annotations['human'])!={uid for uid,r in raw.items() if r['tag']=='human'}:raise ValueError('Human annotation coverage mismatch')
    rows=[];source_files=[DATA,ANNOTATIONS,Path(__file__),UPSTREAM/'dev_hold_split.json',
        UPSTREAM/'chinatravel/symbol_verification/concept_func.py',
        UPSTREAM/'chinatravel/symbol_verification/commonsense_constraint.py',
        CORE/'scripts/chinatravel_parse_plan.py',CORE/'scripts/chinatravel_symbolic_probe.py']
    for uid,merged in sorted(raw.items()):
        path=UPSTREAM/'chinatravel/data/dev_split'/f'{uid}.json';query=read(path);source_files.append(path)
        for key in ('uid','tag','nature_language','hard_logic_py','target_city','days','people_number'):
            if merged[key]!=query[key]:raise ValueError('Canonical/merged mismatch')
        if merged['org']!=query['start_city']:raise ValueError('Origin mismatch')
        rows.append(inspect_query(query,annotations['human'].get(uid,{})))
    selected=select(rows)
    summary={'n_cases':len(rows),'tags':dict(Counter(r['tag'] for r in rows)),
        'current_interface_textually_complete':sum(r['current_interface_textually_complete'] for r in rows),
        'current_interface_has_gaps':sum(bool(r['current_interface_gaps']) for r in rows),
        'unspecified_budget':sum(not r['budget_specified'] for r in rows),
        'evaluation_issue_cases':sum(bool(r['evaluation_issues']) for r in rows),
        'evaluation_issue_case_counts':dict(Counter(kind for r in rows for kind in r['evaluation_issues'])),
        'request_field_case_counts':dict(Counter(field for r in rows for field in {x['field'] for x in r['requirements']})),
        'selected_n':len(selected),'selected_tracks':dict(Counter(x['track'] for x in selected)),
        'model_api_calls':0,'independent_human_reviews':0,
        'scope':'dataset source audit, not model accuracy, task success, DARC effectiveness, or new semantic gold'}
    summary['interface_gap_case_counts']=dict(Counter(field for r in rows for field in set(r['current_interface_gaps'])))
    out.mkdir(parents=True,exist_ok=False)
    dump(out/'audit.json',{'summary':summary,'rows':rows})
    dump(out/'selected_dev10.json',{'selection_rule':'fixed text-requirement strata, first lexicographic unused UID in each; no model outputs or success metrics read',
        'selection_scope':'development engineering plus diagnostic cases; selection after source review, not confirmatory preregistration',
        'cases':selected,'model_calls':0,'collection_status':'not_started',
        'denominator_policy':'10 frozen IDs remain; diagnostic-only cases are not completed model trials and cannot be silently removed',
        'public_inputs':[{'uid':x['uid'],'nature_language':raw[x['uid']]['nature_language']} for x in selected]})
    dump(out/'public_inputs_dev10.json',[{'uid':x['uid'],'nature_language':raw[x['uid']]['nature_language']} for x in selected])
    dump(out/'manifest.json',{'source_hashes':{str(p.resolve().relative_to(ROOT)):sha(p) for p in source_files},
        'model_calls':0,'expected_ids':sorted(dev),'source_review':'all 60 original texts and every DSL parsed; human rows individually annotated',
        'warning':'audit.json and review annotations contain gold; never feed them to model runners'})
    lines=['# 60 条 dev 逐条语义审计','', '本文件是源码/原句审计，不是模型预测或新 gold。完整 DSL 与索引见 audit.json。','']
    for row in rows:
        lines+=['## '+row['uid']+' / '+row['tag'],'',row['nature_language'],'',
            '| 要求 | 原句证据 | 官方覆盖 | DSL 索引（零基） | 说明 |','|---|---|---|---|---|']
        for req in row['requirements']:
            lines.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in [req['field'],req['quote'],req['official_coverage'],','.join(map(str,req['dsl_indices'])) or '无',req['note']])+' |')
        lines+=['','接口缺口：'+(', '.join(row['current_interface_gaps']) or '无；仅表示字段可表达，不代表任务成功。')]
        if row['conflicts']:lines+=['输入冲突：'+json.dumps(row['conflicts'],ensure_ascii=False)]
        lines+=row['interpretation_notes']+['']
    (out/'AUDIT_60.md').write_text('\n'.join(lines)+'\n')
    dump(out/'artifact_hashes.json',{path.name:sha(path) for path in out.iterdir() if path.is_file()})
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',required=True)
    run(Path(parser.parse_args().out).resolve())
