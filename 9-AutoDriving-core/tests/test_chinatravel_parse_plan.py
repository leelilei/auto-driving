import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_parse_plan as p
ct=p.ct


class ParsePlanTests(unittest.TestCase):
    def extracted(self):
        return {'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':1500,
            'evidence':{'start_city':'当前位置上海','target_city':'杭州','days':'一天','people_number':'一个人','budget':'1500'},
            'unsupported_requirements':[]}

    def native(self,value):
        return {'content':[{'type':'tool_use','name':'parse_intent','id':'test','input':value}],
            'stop_reason':'tool_use','usage':{'input_tokens':10,'output_tokens':20}}

    def test_verbatim_evidence_and_duplicate_calls(self):
        public={'nature_language':'当前位置上海。我一个人想去杭州玩一天，预算1500人民币，请给我一个旅行规划。'}
        self.assertEqual(p.decode(self.native(self.extracted()),public),self.extracted())
        value=self.extracted();value['evidence']['budget']='9999'
        with self.assertRaises(ValueError):p.decode(self.native(value),public)
        data=self.native(self.extracted());data['content']*=2
        with self.assertRaises(ValueError):p.decode(data,public)

    def test_original_evaluation_query_keeps_gold_and_origin(self):
        merged=ct.read(ct.DATA)[ct.REGRESSION];canonical=p.evaluation_query(ct.REGRESSION)
        self.assertEqual(canonical['start_city'],merged['org'])
        self.assertEqual(canonical['hard_logic_py'],merged['hard_logic_py'])
        self.assertEqual(canonical['nature_language'],merged['nature_language'])

    def test_wire_boundary_and_full_offline_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'archive';p.prepare(out);seen=[]
            def urlopen(request,**kwargs):
                seen.append(json.loads(request.data))
                return io.BytesIO(ct.dumps(self.native(self.extracted())).encode())
            with patch('llm_client.get_api_key',return_value='offline-placeholder'),patch('urllib.request.urlopen',side_effect=urlopen),ct.offline():
                p.collect(out)
            self.assertEqual(len(seen),1)
            self.assertNotIn('hard_logic_py',ct.dumps(seen))
            self.assertNotIn('offline-placeholder',ct.dumps(ct.read(out/'request.json')))
            self.assertEqual(ct.read(out/'collection.json')['status'],'search_success')
            p.seal(out);first=p.replay(out);second=p.replay(out)
            self.assertEqual(first,second)
            self.assertEqual(first['all_pass_rate'],100)
            (out/'predictions.json').unlink()
            with self.assertRaises(ValueError):p.replay(out)

    def test_unsupported_requirements_stop_without_planning(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'archive';p.prepare(out)
            value=self.extracted();value['unsupported_requirements']=['test unsupported clause']
            with patch('llm_client.get_api_key',return_value='offline-placeholder'),patch('urllib.request.urlopen',return_value=io.BytesIO(ct.dumps(self.native(value)).encode())),ct.offline():
                p.collect(out)
            self.assertEqual(ct.read(out/'collection.json')['status'],'unsupported_or_incomplete_intent')
            self.assertFalse((out/'search').exists())
            self.assertEqual(ct.read(out/'predictions.json'),{ct.REGRESSION:{}})


if __name__=='__main__':unittest.main()
