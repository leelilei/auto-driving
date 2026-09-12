"""Collect the frozen 100-call-per-model ChinaTravel diagnostic."""
import argparse, json, os, time, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_crossmodel100_20260912'
FIELDS=('start_city','target_city','days','people_number','budget','room_count','room_type','cuisine','intercity_mode','attraction_category')
SYSTEM='''Extract the explicitly requested travel constraints and return exactly one JSON object. Required keys: start_city,target_city,days,people_number,budget,room_count,room_type,cuisine,intercity_mode,attraction_category. Use null only when the query does not specify a field. Do not plan an itinerary. Dataset party convention: 我计划/我打算/我想 without a companion means 1; 我和朋友/男朋友/女朋友 means 2; 我们N个人 means N. room_type is 1 for 单床房 and 2 for 双床房. intercity_mode is train or airplane. Only extract an explicit cuisine or attraction category; do not invent proxies. No markdown or commentary.'''

def read(p): return json.loads(Path(p).read_text())
def save(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def body(item,model,anthropic):
    user=json.dumps(item,ensure_ascii=False)
    if anthropic:
        return {'model':model,'system':SYSTEM,'messages':[{'role':'user','content':user}],'temperature':0,'max_tokens':700}
    return {'model':model,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':user}],'temperature':0,'max_tokens':700,'response_format':{'type':'json_object'},'thinking':{'type':'disabled'}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--model',choices=['deepseek','haiku','qwen_flash','gemini3_flash'],required=True); ap.add_argument('--retry-failed',action='store_true'); a=ap.parse_args()
    model={'deepseek':'deepseek-v4-flash','haiku':'claude-haiku-4-5-20251001','qwen_flash':'qwen3.8-flash','gemini3_flash':'gemini-3-flash'}[a.model]; anthropic=a.model=='haiku'
    out=RUN/f"collection_{a.model}{'_retry1' if a.retry_failed else ''}.json"
    if out.exists(): raise ValueError('Refuse overwrite: '+str(out))
    key=os.environ.get('XCODE_API_KEY' if anthropic or a.model in ('qwen_flash','gemini3_flash') else 'DEEPSEEK_API_KEY')
    if not key: raise RuntimeError('required API key unavailable')
    public={x['uid']:x for x in read(RUN/'public_inputs.json')}; schedule=read(RUN/'call_schedule.json'); records=[]
    for item in schedule:
        public_item=public[item['uid']]; payload=body(public_item,model,anthropic); rec={**item,'request':payload,'status':'STARTED','attempts':1}
        try:
            if anthropic:
                url='https://xcode.best/v1/messages'; headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json','User-Agent':'Mozilla/5.0'}
            else:
                if a.model in ('qwen_flash','gemini3_flash'): url='https://xcode.best/v1/chat/completions'
                else: url='https://api.deepseek.com/v1/chat/completions'
                headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'}
            req=urllib.request.Request(url,data=json.dumps(payload,ensure_ascii=False).encode(),headers=headers,method='POST')
            with urllib.request.urlopen(req,timeout=120) as response: env=json.loads(response.read().decode())
            rec['provider_response']=env
            if anthropic: text=''.join(x.get('text','') for x in env.get('content',[]) if x.get('type')=='text')
            else: text=env['choices'][0]['message']['content']
            if a.model in ('qwen_flash','gemini3_flash') and env.get('model') != model: raise ValueError('provider model mismatch: '+str(env.get('model')))
            parsed=json.loads(text)
            if set(parsed)!=set(FIELDS): raise ValueError('JSON keys mismatch')
            rec.update(status='COMPLETE',parsed_intent=parsed)
        except Exception as exc:
            rec.update(status='FAILED',error_type=type(exc).__name__,error=str(exc))
        records.append(rec); print(json.dumps({'model':a.model,'call_index':item['call_index'],'uid':item['uid'],'status':rec['status']},ensure_ascii=False),flush=True)
    save(out,{'status':'COLLECTED','model':model,'provider':'xcode' if anthropic else 'official DeepSeek','logical_calls':100,'complete':sum(r['status']=='COMPLETE' for r in records),'records':records,'retry_policy':'one separately named run; no semantic retry'})

if __name__=='__main__': main()
