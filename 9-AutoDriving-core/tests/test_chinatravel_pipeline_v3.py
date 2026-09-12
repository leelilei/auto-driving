"""Offline native-protocol and archive acceptance; never sends a model request."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_pipeline_v3 as ct


def response(value,phase='query',text=None):
    content=[] if text is None else [{'type':'text','text':text}]
    content.append({'type':'tool_use','id':'offline-id','name':ct.native_tool(phase)['tool_choice']['name'],'input':value})
    return {'model':'claude-haiku-4-5-20251001','content':content,'stop_reason':'tool_use',
            'usage':{'input_tokens':10,'output_tokens':20}}


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)
        self.public={'uid':'test','nature_language':'当前位置上海。我一个人想去杭州玩一天，预算1500人民币，请给我一个旅行规划。'}

    @contextlib.contextmanager
    def transport(self,responses):
        replies=iter(responses);payloads=[]
        def urlopen(request,**kwargs):
            payloads.append(json.loads(request.data))
            value=next(replies)
            if isinstance(value,Exception):raise value
            return io.BytesIO(ct.dumps(value).encode())
        with patch('llm_client.get_api_key',return_value='offline-key'),patch('urllib.request.urlopen',side_effect=urlopen),ct.offline():
            yield ct.NativeClient(),payloads

    def test_native_action_and_final_official_schema(self):
        fixture=ct.read(ROOT/'docs/experiments/chinatravel_setup/codex_validation/fixture_candidate.json')['result']
        # Gold-built fixture is a fake response ONLY in this offline acceptance test.
        # It is never included in a prompt, live model context or candidate selection.
        action={'kind':'tool','name':'attractions_keys','arguments':{'city':'杭州'}}
        with self.transport([response(action)]*8+[response(fixture,'final')]) as (client,payloads):
            prediction,result=ct.collect_case(self.public,client,self.out)
        self.assertEqual(result['calls'],9)
        self.assertEqual(result['query_calls'],8)
        self.assertEqual(result['status'],'schema_valid')
        self.assertEqual(prediction,fixture)
        self.assertEqual(payloads[-1]['tool_choice']['name'],'submit_itinerary')
        self.assertNotIn('hard_logic_py',ct.dumps(payloads))

    def test_native_text_is_separate_not_parsed_or_executed(self):
        action={'kind':'tool','name':'attractions_keys','arguments':{'city':'杭州'}}
        original=response(action,text='```json\n{"kind":"tool","name":"__import__"}\n```')
        self.assertEqual(ct.strict_json(ct.native_response(original,'query')),action)
        self.assertEqual(len(original['content']),2)
        with self.transport([original,response({'kind':'finish'}),response({},'final')]) as (client,payloads):
            _,result=ct.collect_case(self.public,client,self.out)
        record=ct.read(self.out/'requests/test/call_001.json')
        self.assertEqual(record['provider_response'],original)
        self.assertEqual(result['calls'],3)
        self.assertEqual(json.loads((self.out/'tool_trace.jsonl').read_text().splitlines()[0])['observation']['status'],'ok')

    def test_multiple_wrong_or_truncated_native_tools_rejected(self):
        variants=[]
        multiple=response({'kind':'finish'});multiple['content']*=2;variants.append(multiple)
        wrong=response({'kind':'finish'});wrong['content'][0]['name']='wrong';variants.append(wrong)
        truncated=response({'kind':'finish'});truncated['stop_reason']='max_tokens';variants.append(truncated)
        variants.append({'content':[{'type':'text','text':'{"kind":"finish"}'}],'stop_reason':'end_turn'})
        for variant in variants:
            with self.subTest(variant=variant):
                self.assertIn('native_protocol_error',ct.strict_json(ct.native_response(variant,'query')))

    def test_v2_real_failures_cannot_be_executed_as_native_calls(self):
        old=ROOT/'9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_json_v2_dev3'
        variants=[]
        for path in sorted((old/'requests').rglob('*.json')):
            variants.append({'content':[{'type':'text','text':ct.read(path)['response']}],'stop_reason':'end_turn'})
        self.assertEqual(len(variants),2)
        with self.transport(variants) as (client,payloads):
            _,result=ct.collect_case(self.public,client,self.out)
        self.assertEqual(result['status'],'two_consecutive_protocol_errors')
        self.assertEqual(result['calls'],2)
        correction=json.loads(payloads[1]['messages'][0]['content'])['protocol_correction']
        self.assertIn('native_protocol_error',correction['previous_response_prefix'])
        self.assertIn('上次动作未执行',correction['instruction'])

    def test_wire_gold_sentinel_and_tool_budget_accounting(self):
        source=dict(self.public,hard_logic_py=['V3_GOLD_SENTINEL'],nested={'answer':'V3_GOLD_SENTINEL'})
        with self.transport([response({'kind':'finish'}),response({},'final')]) as (client,payloads):
            _,result=ct.collect_case(ct.v1.model_input(source),client,self.out)
        charged=0
        for i,payload in enumerate(payloads,1):
            self.assertNotIn('V3_GOLD_SENTINEL',ct.dumps(payload))
            self.assertIn(self.public['nature_language'],payload['messages'][0]['content'])
            record=ct.read(self.out/f'requests/test/call_{i:03d}.json')
            content_chars=len(payload['system'])+len(payload['messages'][0]['content'])
            tool_chars=len(ct.dumps({key:payload[key] for key in ('tools','tool_choice')}))
            self.assertEqual(record['input_chars'],content_chars)
            self.assertEqual(record['charged_chars'],content_chars+tool_chars)
            self.assertNotIn('offline-key',ct.dumps(record))
            charged+=record['charged_chars']
        self.assertEqual(charged,result['chars'])

    def test_failed_request_and_query_reservation(self):
        with self.transport([TimeoutError('injected')]) as (client,payloads):
            _,result=ct.collect_case(self.public,client,self.out)
        self.assertEqual(result['calls'],1)
        self.assertEqual(result['status'],'collection_error:TimeoutError')
        self.assertEqual(ct.read(self.out/'requests/test/call_001.json')['telemetry']['attempts'],1)
        with self.transport([response({'kind':'finish'})]) as (client,payloads):
            recorder=ct.Recorder(client,self.out,'boundary');recorder.query_chars=110000
            with self.assertRaises(ct.BudgetStop):recorder.send(*ct.context(self.public,[],'query'),'query')
            self.assertEqual(payloads,[])
            recorder.chars=160000
            with self.assertRaises(ct.BudgetStop):recorder.send(*ct.context(self.public,[],'final'),'final')

    def test_frozen_archive_replay_and_response_tamper(self):
        out=self.out/'archive';ct.prepare(out)
        public=ct.read(out/'public_inputs.json')[0]
        with self.transport([response({'kind':'tool','name':'attractions_keys','arguments':{'city':'杭州'}}),response({'kind':'finish'}),response({},'final')]) as (client,payloads):
            _,case=ct.collect_case(public,client,out)
        collection=ct.read(out/'collection.json');collection['cases'][public['uid']]=case;ct.write(out/'collection.json',collection)
        ct.score_command(out);ct.seal(out)
        self.assertEqual(ct.replay(out),ct.replay(out))
        self.assertEqual(ct.read(out/'official_score.json')['n_expected'],3)
        copy=self.out/'copy';shutil.copytree(out,copy)
        path=next((copy/'requests').rglob('*.json'));record=ct.read(path)
        record['provider_response']['content'][0]['input']={'kind':'finish'};ct.write(path,record)
        with self.assertRaisesRegex(ValueError,'integrity'):ct.replay(copy)


if __name__=='__main__':unittest.main()
