"""Offline integration acceptance for the JSON adapter; no live model calls."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_pipeline_v2 as ct


class Fake:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.telemetry = []
        self.seen = []

    def complete(self,system,user):
        self.seen.append((system,user))
        response = next(self.responses)
        if isinstance(response,Exception):
            raise response
        return response


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = ct.Sandbox()

    def trace(self,name,args):
        return ct.action_trace(ct.dumps({'kind':'tool','name':name,'arguments':args}),self.sandbox)

    def test_real_tool_and_pagination(self):
        first = self.trace('attractions_select',{'city':'杭州'})
        second = self.trace('attractions_select',{'city':'杭州','page':1})
        self.assertEqual(first['observation']['status'],'ok')
        self.assertEqual(first['observation']['page_size'],5)
        self.assertNotEqual(first['observation']['data'],second['observation']['data'])
        expected = json.loads(self.sandbox.env.attractions.select('杭州','name',lambda x:True).head(5).to_json(orient='records',force_ascii=False))
        self.assertEqual(first['observation']['data'],expected)

    def test_filter_and_no_match(self):
        actual = self.trace('attractions_select',{'city':'杭州','filters':[{'key':'name','op':'eq','value':'NONEXISTENT'}]})
        self.assertEqual(actual['observation']['status'],'no_match')
        contains = self.trace('attractions_select',{'city':'杭州','filters':[{'key':'name','op':'contains','value':'西湖'}]})
        self.assertEqual(contains['observation']['status'],'ok')
        self.assertTrue(all('西湖' in row['name'] for row in contains['observation']['data']))

    def test_unknown_entity_distinct_from_internal_error(self):
        args = {'city':'杭州','start':'NO_SUCH_POINT','end':'杭州东站','start_time':'08:00','transport_type':'taxi'}
        result = self.trace('goto',args)
        self.assertEqual(result['observation']['status'],'unknown_entity')
        self.assertEqual(result['observation']['name'],'NO_SUCH_POINT')
        with patch.object(self.sandbox.env.intercitytransport,'select',side_effect=RuntimeError('offline injected bug')):
            result = self.trace('intercity_transport_select',{'start_city':'上海','end_city':'杭州','intercity_type':'train'})
        self.assertEqual(result['observation']['status'],'tool_internal_error')
        self.assertEqual(result['observation']['error_type'],'RuntimeError')

    def test_invalid_json_multiple_actions_and_duplicate_keys(self):
        for raw in [r'{\"kind\":\"finish\"}', '[]', '{"kind":"finish"}{"kind":"finish"}',
                    '{"kind":"finish","kind":"tool"}', '{"kind":"other"}', '{"kind":"tool","name":NaN}']:
            with self.subTest(raw=raw),patch.object(self.sandbox,'dispatch') as dispatch:
                result = ct.action_trace(raw,self.sandbox)
                self.assertEqual(result['raw_response'],raw)
                self.assertEqual(result['observation']['status'],'protocol_error')
                dispatch.assert_not_called()

    def test_fixed_fence_conversion(self):
        raw = '```json\n{"kind":"finish"}\n```'
        result = ct.action_trace(raw,self.sandbox)
        self.assertEqual(result['raw_response'],raw)
        self.assertEqual(result['transformation'],'outer_markdown_fence')
        self.assertEqual(result['observation']['status'],'finish')
        self.assertEqual(ct.action_trace('prose\n'+raw,self.sandbox)['observation']['status'],'protocol_error')

    def test_argument_errors_and_dangerous_expressions(self):
        cases = [
            ('__import__',{},'unknown_tool'),
            ('goto',{},'missing_argument'),
            ('attractions_select',{'city':42},'argument_type'),
            ('attractions_select',{'city':'杭州','page':True},'argument_type'),
            ('attractions_select',{'city':'杭州','func':'lambda x: __import__("os")'},'unknown_argument'),
            ('attractions_select',{'city':'杭州','filters':[{'key':'name','op':'eval','value':'__import__("os")'}]},'invalid_filter'),
            ('attractions_select',{'city':'杭州','filters':[{'key':'BAD','op':'eq','value':'x'}]},'invalid_filter'),
        ]
        for name,args,code in cases:
            with self.subTest(code=code):
                result = self.trace(name,args)
                self.assertEqual(result['observation']['code'],code)
                self.assertIsNone(result['dispatched_call'])


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)
        self.public = {'uid':'test','nature_language':'原句：上海出发，去杭州一天，预算1500元，不删减要求。'}

    def test_gold_sentinel_at_actual_request_and_feedback_boundary(self):
        gold = dict(self.public,hard_logic_py=['INDEPENDENT_GOLD_SENTINEL'],nested={'answer':'INDEPENDENT_GOLD_SENTINEL'})
        fake = Fake(['invalid',ct.dumps({'kind':'tool','name':'attractions_keys','arguments':{'city':'杭州'}}),'{"kind":"finish"}','{}'])
        _,result = ct.collect_case(ct.v1.model_input(gold),fake,self.out)
        self.assertEqual(result['calls'],4)
        self.assertEqual(result['status'],'final_schema_invalid')
        for request in (self.out/'requests').rglob('*.json'):
            record = ct.read(request)
            boundary = ct.dumps({'system':record['system'],'user':record['user']})
            self.assertIn(self.public['nature_language'],record['user'])
            self.assertNotIn('INDEPENDENT_GOLD_SENTINEL',boundary)
        traces = (self.out/'tool_trace.jsonl').read_text()
        self.assertNotIn('INDEPENDENT_GOLD_SENTINEL',traces)
        self.assertIn('official_schema',fake.seen[-1][1])

    def test_consecutive_failures_hard_stop(self):
        fake = Fake(['invalid','invalid','{}'])
        _,result = ct.collect_case(self.public,fake,self.out)
        self.assertEqual(result['status'],'two_consecutive_protocol_errors')
        self.assertEqual(result['calls'],2)
        self.assertFalse(any(json.loads(user)['phase']=='final' for _,user in fake.seen))

    def test_serialized_http_request_gold_isolation(self):
        import io
        import llm_client
        config = llm_client.resolve_config(ct.CONFIG)
        payloads = []
        replies = iter(['invalid','{"kind":"finish"}','{}'])
        def urlopen(request, **kwargs):
            payloads.append(json.loads(request.data))
            return io.BytesIO(json.dumps({'content':[{'type':'text','text':next(replies)}],
                                         'usage':{'input_tokens':1,'output_tokens':1}}).encode())
        with patch.object(llm_client,'get_api_key',return_value='offline-test-placeholder'), patch('urllib.request.urlopen',side_effect=urlopen),ct.offline():
            client = llm_client.LLM(config=config)
            source = dict(self.public,hard_logic_py=['HTTP_GOLD_SENTINEL'],answer='HTTP_GOLD_SENTINEL')
            _,result = ct.collect_case(ct.v1.model_input(source),client,self.out)
        self.assertEqual(result['calls'],3)
        self.assertEqual(len(payloads),3)
        for index,payload in enumerate(payloads,1):
            self.assertNotIn('HTTP_GOLD_SENTINEL',json.dumps(payload))
            self.assertIn(self.public['nature_language'],payload['messages'][0]['content'])
            record = ct.read(self.out/f'requests/test/call_{index:03d}.json')
            self.assertEqual(record['wire_payload'],payload)
            self.assertEqual(record['input_chars'],len(payload['system'])+len(payload['messages'][0]['content']))
            self.assertNotIn('offline-test-placeholder',json.dumps(record))

    def test_failed_transport_is_counted_and_persisted(self):
        fake = Fake([TimeoutError('injected')])
        _,result = ct.collect_case(self.public,fake,self.out)
        record = ct.read(self.out/'requests/test/call_001.json')
        self.assertEqual(result['calls'],1)
        self.assertEqual(result['chars'],len(record['system'])+len(record['user']))
        self.assertEqual(record['error_type'],'TimeoutError')

    def test_query_reservation_and_hard_limits(self):
        fake = Fake(['{}']*12)
        recorder = ct.Recorder(fake,self.out,'test')
        recorder.send('s','x'*109999,'query')
        with self.assertRaises(ct.BudgetStop):
            recorder.send('s','','query')
        self.assertEqual(recorder.calls,1)
        recorder.send('s','x'*49999,'final')
        self.assertEqual(recorder.chars,160000)
        with self.assertRaises(ct.BudgetStop):
            recorder.send('s','','final')
        recorder.started -= 901
        with self.assertRaises(ct.BudgetStop):
            recorder.send('','','final')
        self.assertEqual(len(fake.seen),2)

    def test_eight_queries_then_final(self):
        action = ct.dumps({'kind':'tool','name':'attractions_keys','arguments':{'city':'杭州'}})
        fake = Fake([action]*8+['{}'])
        _,result = ct.collect_case(self.public,fake,self.out)
        self.assertEqual(result['calls'],9)
        self.assertEqual(result['query_calls'],8)
        self.assertEqual(json.loads(fake.seen[-1][1])['phase'],'final')

    def test_final_raw_json_not_repaired(self):
        fake = Fake(['{"kind":"finish"}','```json\n{}\n```'])
        prediction,result = ct.collect_case(self.public,fake,self.out)
        self.assertEqual(result['status'],'final_invalid_json')
        self.assertEqual(prediction,{})

    def test_deterministic_fact_retention(self):
        facts = [{'parsed_action':{'kind':'finish'},'observation':{'data':'x'*14000}} for _ in range(4)]
        system,user = ct.context(self.public,facts,'final')
        parsed = json.loads(user)
        self.assertEqual(parsed['omitted_trace_indices'],[0,1])
        self.assertEqual([f['trace_index'] for f in parsed['facts']],[2,3])
        self.assertLess(len(system)+len(user),50000)
        self.assertEqual((system,user),ct.context(self.public,facts,'final'))

    def test_physical_deadline_enforced(self):
        import time
        with self.assertRaises(TimeoutError):
            with ct.deadline(0.01):
                time.sleep(0.1)


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.temp.name)/'archive'
        ct.prepare(cls.out)
        public = ct.read(cls.out/'public_inputs.json')[0]
        prediction,case = ct.collect_case(public,Fake(['{"kind":"finish"}','{}']),cls.out)
        collection = ct.read(cls.out/'collection.json')
        collection['cases'][public['uid']] = case
        ct.write(cls.out/'collection.json',collection)
        ct.score_command(cls.out)
        ct.seal(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_repeated_offline_replay_and_complete_ids(self):
        first = ct.replay(self.out)
        second = ct.replay(self.out)
        self.assertEqual(first,second)
        self.assertEqual(first['physical_requests'],2)
        score = ct.read(self.out/'official_score.json')
        self.assertEqual(score['n_expected'],3)
        self.assertEqual(len(score['per_case']),3)

    def test_deleted_prediction_and_emptied_hash_map_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'copy'; shutil.copytree(self.out,out)
            (out/'predictions.json').unlink()
            with self.assertRaises((ValueError,FileNotFoundError)):
                ct.replay(out)
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'copy'; shutil.copytree(self.out,out)
            ct.write(out/'manifest_hashes.json',{})
            with self.assertRaisesRegex(ValueError,'roles'):
                ct.replay(out)

    def test_modified_response_and_missing_trace_detected(self):
        for role in ['response','trace']:
            with self.subTest(role=role),tempfile.TemporaryDirectory() as temp:
                out = Path(temp)/'copy'; shutil.copytree(self.out,out)
                if role=='response':
                    path = next((out/'requests').rglob('*.json'))
                    record = ct.read(path); record['response']='changed'; ct.write(path,record)
                else:
                    (out/'tool_trace.jsonl').write_text('')
                with self.assertRaisesRegex(ValueError,'integrity'):
                    ct.replay(out)

    def test_evaluator_source_substitution_detected(self):
        real_sha = ct.sha
        def substituted(path):
            if str(path).endswith('evaluation/hard_constraint.py'):
                return '0'*64
            return real_sha(path)
        with patch.object(ct,'sha',substituted),self.assertRaisesRegex(ValueError,'source/data/config'):
            ct.replay(self.out)

    def test_request_deletion_even_if_hash_entry_removed(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'copy'; shutil.copytree(self.out,out)
            path = next((out/'requests').rglob('*.json'))
            hashes = ct.read(out/'manifest_hashes.json'); hashes.pop(str(path.relative_to(out)))
            path.unlink(); ct.write(out/'manifest_hashes.json',hashes)
            with self.assertRaisesRegex(ValueError,'roles'):
                ct.replay(out)


if __name__=='__main__':
    unittest.main()
