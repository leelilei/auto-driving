"""XCODE-compatible Stage-3 collector using plain Messages JSON (no tools)."""
import json, os, re, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'; SCRIPTS=ROOT/'9-AutoDriving-core/scripts'
SYSTEM='Return exactly one JSON object with keys start_city,target_city,days,people_number,budget,room_count,room_type,cuisine,intercity_mode,attraction_category. Use null for unspecified. Do not invent requirements. No markdown or commentary.'
FIELDS=('start_city','target_city','days','people_number','budget','room_count','room_type','cuisine','intercity_mode','attraction_category')
def main():
    if not os.getenv('XCODE_API_KEY'):
        try: os.environ['XCODE_API_KEY']=subprocess.check_output(['security','find-generic-password','-s','XCODE_API_KEY','-w'],text=True).strip()
        except Exception as e: raise RuntimeError('XCODE_API_KEY unavailable') from e
    import sys;sys.path.insert(0,str(SCRIPTS));import chinatravel_pipeline_v3 as ct
    config=ct.NativeClient().config; key=os.environ['XCODE_API_KEY']; out=[]
    for item in json.loads((RUN/'public_inputs.json').read_text()):
        rec={'uid':item['uid'],'max_requests':1}
        try:
            body={'model':config.model,'system':SYSTEM,'messages':[{'role':'user','content':json.dumps(item,ensure_ascii=False)}],'max_tokens':300,'temperature':0}
            req=__import__('urllib.request',fromlist=['Request']).Request(config.base_url+'/v1/messages',data=json.dumps(body).encode(),method='POST',headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'})
            with __import__('urllib.request',fromlist=['urlopen']).urlopen(req,timeout=60) as response: envelope=json.loads(response.read().decode())
            rec['provider_response']=envelope; text=''.join(x.get('text','') for x in envelope.get('content',[]) if x.get('type')=='text'); text=re.sub(r'^```(?:json)?\s*|\s*```$','',text.strip(),flags=re.I)
            parsed=json.loads(text)
            if set(parsed)!=set(FIELDS): raise ValueError('JSON keys mismatch')
            if parsed['cuisine']=='null': parsed['cuisine']=None
            if parsed['attraction_category']=='null': parsed['attraction_category']=None
            if parsed['room_type']=='null': parsed['room_type']=None
            rec.update(status='JSON_VALID',parsed_intent=parsed)
        except Exception as e: rec.update(status='FAILED',error_type=type(e).__name__,error=str(e))
        out.append(rec)
        if rec.get('error','').startswith('HTTP Error 401'): break
    report={'status':'COLLECTED_JSON_COMPAT','model_api_calls':len(out),'json_valid':sum(x['status']=='JSON_VALID' for x in out),'records':out}
    (RUN/'collection_json_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
