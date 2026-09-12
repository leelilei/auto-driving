"""Deterministic, evidence-preserving intent normalization for interface audit.

This is an offline parser for development checks, not a replacement for the
frozen model parser. Missing budget remains ``None`` and unsupported clauses
are retained verbatim.
"""
import re
import json

FIELDS = ('start_city', 'target_city', 'days', 'people_number', 'budget', 'room_count', 'room_type', 'cuisine', 'intercity_mode', 'attraction_category')
SYSTEM='Extract explicit travel fields from the original query. Return one parse_intent tool call; preserve unsupported requirements and never invent missing values.'
def tool_spec():
    props={k:{'type':['string','null']} for k in FIELDS}
    props.update(days={'type':['integer','null'],'minimum':1},people_number={'type':['integer','null'],'minimum':1},budget={'type':['number','null'],'minimum':0},room_count={'type':['integer','null'],'minimum':1},room_type={'type':['integer','null'],'enum':[1,2,None]},intercity_mode={'type':['string','null'],'enum':['train','airplane',None]})
    return {'tools':[{'name':'parse_intent','description':'Extract fields','input_schema':{'type':'object','properties':props,'required':FIELDS,'additionalProperties':False}}], 'tool_choice':{'type':'tool','name':'parse_intent','disable_parallel_tool_use':True}}
def validate(parsed, original):
    if not isinstance(parsed,dict): raise ValueError('intent must be object')
    for k in FIELDS:
        if k not in parsed: raise ValueError('missing '+k)
    for k in ('cuisine','attraction_category'):
        if parsed[k] is not None and (not isinstance(parsed[k],str) or not parsed[k].strip() or parsed[k].strip().lower() == 'null'):
            raise ValueError('invalid '+k)
    if parsed['room_type'] is not None and parsed['room_type'] not in (1,2): raise ValueError('room_type must be 1 or 2')
    if parsed['intercity_mode'] is not None and parsed['intercity_mode'] not in ('train','airplane'): raise ValueError('invalid intercity_mode')
    for k in ('days','people_number','room_count'):
        if parsed[k] is not None and (type(parsed[k]) is not int or parsed[k] < 1): raise ValueError('invalid '+k)
    if parsed['budget'] is not None and (isinstance(parsed['budget'],bool) or not isinstance(parsed['budget'],(int,float)) or parsed['budget'] < 0): raise ValueError('invalid budget')
    return parsed

def compile_extended(parsed):
    clauses = compile_intent(parsed)
    if parsed.get('room_count') is not None: clauses.append('result=True\nfor activity in allactivities(plan):\n if activity_type(activity)=="accommodation" and room_count(activity)!=%d: result=False' % parsed['room_count'])
    if parsed.get('room_type') is not None: clauses.append('result=True\nfor activity in allactivities(plan):\n if activity_type(activity)=="accommodation" and room_type(activity)!=%d: result=False' % parsed['room_type'])
    if parsed.get('intercity_mode') is not None: clauses.append('result=True\nfor activity in allactivities(plan):\n if activity_type(activity) in ["train","airplane"] and intercity_transport_type(activity)!="%s": result=False' % parsed['intercity_mode'])
    if parsed.get('cuisine'):
        value=json.dumps(parsed['cuisine'],ensure_ascii=False)
        clauses.append('found=False\nfor activity in allactivities(plan):\n if activity_type(activity) in ["breakfast","lunch","dinner"] and restaurant_type(activity,target_city(plan))==%s: found=True\nresult=found' % value)
    if parsed.get('attraction_category'):
        value=json.dumps(parsed['attraction_category'],ensure_ascii=False)
        clauses.append('found=False\nfor activity in allactivities(plan):\n if activity_type(activity)=="attraction" and attraction_type(activity,target_city(plan))==%s: found=True\nresult=found' % value)
    return clauses

def compile_intent(parsed):
    """Compile only resolved base fields; omitted budget adds no cost clause."""
    required = ('start_city','target_city','days','people_number')
    if any(parsed.get(k) is None for k in required):
        raise ValueError('Missing required field')
    clauses=[f"result=(day_count(plan)=={parsed['days']})",
             f"result=(people_count(plan)=={parsed['people_number']})"]
    if parsed.get('budget') is not None:
        clauses.append('total=0\nfor activity in allactivities(plan):\n total+=activity_cost(activity)\n total+=innercity_transport_cost(activity_transports(activity))\nresult=(total<=%r)' % parsed['budget'])
    return clauses

def parse(text):
    header = re.search(r'当前位置([^，。,]+)[，,]目标位置([^，。,]+)[，,]旅行人数(\d+)[，,]旅行天数(\d+)', text)
    if header:
        start, target, people, days = header.group(1), header.group(2), int(header.group(3)), int(header.group(4))
    else:
        m = re.search(r'当前位置([^。]+)。.*?(?:打算去|计划去|想去|去)([^，。]+?)玩([一二两三四五六七\d]+)天', text)
        if not m:
            raise ValueError('Cannot identify route and duration')
        start, target, token = m.group(1), m.group(2), m.group(3)
        days = int(token) if token.isdigit() else {'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7}[token]
        party = re.search(r'(?:我和(?:朋友|女朋友|男朋友)|我们(\d+)个人|我一个人)', text)
        people = int(party.group(1)) if party and party.group(1) else (1 if '我一个人' in text else 2)
    budget_match = re.search(r'(?:预算|预算为|预算是)(\d+(?:\.\d+)?)\s*(?:人民币|元)?', text)
    budget = float(budget_match.group(1)) if budget_match else None
    evidence = {
        'start_city': start, 'target_city': target,
        'days': ('旅行天数' + str(days)) if header else ('玩' + re.search(r'玩([一二两三四五六七\d]+)天', text).group(1) + '天'),
        'people_number': ('旅行人数' + str(people)) if header else (re.search(r'我和(?:朋友|女朋友|男朋友)', text).group(0) if re.search(r'我和(?:朋友|女朋友|男朋友)', text) else '我'),
        'budget': budget_match.group(0) if budget_match else ''}
    return {'start_city': start, 'target_city': target, 'days': days, 'people_number': people,
            'budget': budget, 'evidence': evidence,
            'unsupported_requirements': _unsupported(text, budget_match)}

def _unsupported(text, budget_match):
    clauses = []
    for pattern in (r'市内[^。]*?(?:地铁|出租车)', r'开[一二三四]间[^，。]+', r'选择(?:火车|飞机)出行',
                    r'想吃[^，。]+', r'希望酒店[^，。]+', r'想欣赏[^，。]+', r'适合带小朋友[^，。]*'):
        clauses.extend(m.group(0) for m in re.finditer(pattern, text))
    return sorted(set(clauses))
