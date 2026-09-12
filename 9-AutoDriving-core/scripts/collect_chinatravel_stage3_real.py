"""Collect six fixed intents with at most one native request each."""
import json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'9-AutoDriving-core/data/chinatravel_stage3_fixed6'; SCRIPTS=ROOT/'9-AutoDriving-core/scripts'
def main():
    if not os.getenv('XCODE_API_KEY'):
        try: os.environ['XCODE_API_KEY']=subprocess.check_output(['security','find-generic-password','-s','XCODE_API_KEY','-w'],text=True).strip()
        except Exception as e: raise RuntimeError('XCODE_API_KEY unavailable in environment and Keychain') from e
    import sys; sys.path.insert(0,str(SCRIPTS)); import chinatravel_pipeline_v3 as ct
    import chinatravel_parse_plan_v4 as v4, urllib.request, time
    from llm_client import resolve_config, get_api_key
    config=resolve_config(ct.CONFIG); key=get_api_key(config.provider,config.api_key_env)
    out=[]
    for item in json.loads((RUN/'public_inputs.json').read_text()):
        public=item; rec={'uid':item['uid'],'max_requests':1}
        try:
            body={'model':config.model,'system':v4.SYSTEM,'messages':[{'role':'user','content':json.dumps(public,ensure_ascii=False)}],'max_tokens':4096,'temperature':0.0,**v4.tool_spec()}
            req=urllib.request.Request(config.base_url.rstrip('/')+'/v1/messages',data=json.dumps(body).encode(),method='POST',headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'})
            started=time.monotonic()
            with urllib.request.urlopen(req,timeout=60) as response: envelope=json.loads(response.read().decode())
            blocks=[b for b in envelope.get('content',[]) if b.get('type')=='tool_use']
            rec['provider_response']=envelope
            if envelope.get('stop_reason')!='tool_use' or len(blocks)!=1 or blocks[0].get('name')!='parse_intent': raise ValueError('parse_intent protocol failure')
            parsed=blocks[0]['input']
            for key in ('cuisine','attraction_category','room_type'):
                if parsed.get(key) == 'null': parsed[key] = None
            parsed=v4.validate(parsed,public['nature_language'])
            rec.update(status='CONTRACT_VALID',parsed_intent=parsed,latency_seconds=time.monotonic()-started)
        except Exception as e: rec.update(status='FAILED',error_type=type(e).__name__,error=str(e))
        out.append(rec)
        if rec.get('error','').startswith('HTTP Error 401') or rec.get('error','').startswith('HTTP Error 403') or rec.get('error','').startswith('HTTP Error 429'):
            break
    report={'status':'COLLECTED','n_cases':6,'model_api_calls':len(out),'contract_valid':sum(x['status']=='CONTRACT_VALID' for x in out),'stopped_on_auth_or_rate_limit':len(out)<6,'records':out}
    (RUN/'collection_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
