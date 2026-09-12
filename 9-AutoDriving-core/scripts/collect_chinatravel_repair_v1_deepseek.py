"""Fresh bounded six-case Repair v1 parse via official DeepSeek."""
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / '9-AutoDriving-core/data/chinatravel_stage3_fixed6/public_inputs.json'
OUT = ROOT / '9-AutoDriving-core/data/chinatravel_repair_v1_deepseek6_retry1'
FIELDS = ('start_city','target_city','days','people_number','budget','room_count',
          'room_type','cuisine','intercity_mode','attraction_category')
SYSTEM = '''Extract the explicitly requested travel constraints and return exactly one JSON object.
Required keys: start_city,target_city,days,people_number,budget,room_count,room_type,cuisine,intercity_mode,attraction_category.
Use null only when the query does not specify a field. Do not plan an itinerary.
Dataset party convention: 我计划/我打算/我想 without a companion means 1; 我和朋友/男朋友/女朋友 means 2; 我们N个人 means N.
room_type is 1 for 单床房 and 2 for 双床房. intercity_mode is train or airplane.
Only extract an explicit cuisine or attraction category; do not invent proxies. No markdown or commentary.'''


def main():
    if OUT.exists():
        raise ValueError('Refuse overwrite: ' + str(OUT))
    key = os.environ.get('DEEPSEEK_API_KEY')
    if not key:
        raise RuntimeError('DEEPSEEK_API_KEY unavailable')
    OUT.mkdir()
    public = json.loads(INPUTS.read_text())
    records = []
    for item in public:
        body = {'model':'deepseek-v4-flash','messages':[
            {'role':'system','content':SYSTEM},
            {'role':'user','content':json.dumps(item,ensure_ascii=False)}],
            'temperature':0,'max_tokens':700,'response_format':{'type':'json_object'},
            'thinking':{'type':'disabled'}}
        rec = {'uid':item['uid'],'request':body,'max_requests':1,'status':'STARTED'}
        try:
            request = urllib.request.Request('https://api.deepseek.com/v1/chat/completions',
                data=json.dumps(body,ensure_ascii=False).encode(), method='POST',
                headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=60) as response:
                envelope = json.loads(response.read().decode())
            rec['provider_response'] = envelope
            parsed = json.loads(envelope['choices'][0]['message']['content'])
            if set(parsed) != set(FIELDS):
                raise ValueError('JSON keys mismatch')
            rec.update(status='COMPLETE',parsed_intent=parsed)
        except Exception as exc:
            rec.update(status='FAILED',error_type=type(exc).__name__,error=str(exc))
        records.append(rec)
    report = {'status':'COLLECTED','model':'deepseek-v4-flash',
              'provider':'official DeepSeek','model_api_calls':len(records),
              'complete':sum(r['status']=='COMPLETE' for r in records),
              'prompt_policy':'dataset party convention disclosed in system prompt',
              'records':records}
    (OUT/'collection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'model_api_calls':len(records),'complete':report['complete'],
                      'statuses':[(r['uid'],r['status']) for r in records]},ensure_ascii=False))


if __name__ == '__main__':
    main()
