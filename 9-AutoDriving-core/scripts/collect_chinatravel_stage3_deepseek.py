"""ChinaTravel six-case collector via official DeepSeek Chat Completions."""
import json, os, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'; SCRIPTS=ROOT/'9-AutoDriving-core/scripts'
SYSTEM='Return exactly one JSON object with keys start_city,target_city,days,people_number,budget,room_count,room_type,cuisine,intercity_mode,attraction_category. Use null for unspecified. No markdown or commentary.'
FIELDS=('start_city','target_city','days','people_number','budget','room_count','room_type','cuisine','intercity_mode','attraction_category')
def main():
    key=os.environ.get('DEEPSEEK_API_KEY')
    if not key: raise RuntimeError('DEEPSEEK_API_KEY unavailable')
    import sys;sys.path.insert(0,str(SCRIPTS));import chinatravel_parse_plan_v4 as v4
    out=[]
    for item in json.loads((RUN/'public_inputs.json').read_text()):
        rec={'uid':item['uid'],'max_requests':1}
        try:
            body={'model':'deepseek-v4-flash','messages':[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(item,ensure_ascii=False)}],'temperature':0,'max_tokens':700,'response_format':{'type':'json_object'},'thinking':{'type':'disabled'}}
            req=urllib.request.Request('https://api.deepseek.com/v1/chat/completions',data=json.dumps(body,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=60) as response: envelope=json.loads(response.read().decode())
            rec['provider_response']=envelope; content=envelope['choices'][0]['message']['content']; parsed=json.loads(content)
            if set(parsed)!=set(FIELDS): raise ValueError('JSON keys mismatch')
            for k in ('room_type','cuisine','attraction_category'):
                if parsed.get(k)=='null': parsed[k]=None
            parsed['room_type']={'单床房':1,'双床房':2}.get(parsed.get('room_type'),parsed.get('room_type'))
            parsed['intercity_mode']={'火车':'train','飞机':'airplane'}.get(parsed.get('intercity_mode'),parsed.get('intercity_mode'))
            rec.update(status='JSON_VALID',parsed_intent=v4.validate(parsed,item['nature_language']))
        except Exception as e: rec.update(status='FAILED',error_type=type(e).__name__,error=str(e))
        out.append(rec)
        if rec.get('error','').startswith('HTTP 401'): break
    report={'status':'COLLECTED_DEEPSEEK_OFFICIAL','model_api_calls':len(out),'json_valid':sum(x['status']=='JSON_VALID' for x in out),'records':out}
    (RUN/'collection_deepseek_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
