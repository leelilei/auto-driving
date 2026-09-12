"""Requires the isolated ChinaTravel environment and pinned local sandbox."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('ct_pipeline', ROOT/'9-AutoDriving-core/scripts/chinatravel_pipeline.py')
ct = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ct)

class BoundaryTests(unittest.TestCase):
    def test_input_whitelist(self):
        q={'uid':'x','nature_language':'原句完整保留','hard_logic_py':['SENTINEL'], 'budget':'SENTINEL','nested':{'answer':'SENTINEL'}}
        self.assertEqual(ct.model_input(q),{'uid':'x','nature_language':'原句完整保留'})
        self.assertNotIn('SENTINEL',json.dumps(ct.model_input(q)))

    def test_missing_text_fails(self):
        with self.assertRaises(ValueError):ct.model_input({'uid':'x','nature_language':''})

    def test_actual_tool_executor(self):
        from chinatravel.environment.world_env import WorldEnv
        with ct.offline():
            result=WorldEnv(lang='zh')('attractions_keys("杭州")')
            self.assertTrue(result['success'])
            self.assertTrue(result['data'])

    def test_bridge_and_budget(self):
        class Fake:
            telemetry=[]
            def complete(self,system,user):
                self.seen=(system,user)
                return 'attractions_keys("杭州")'
        with tempfile.TemporaryDirectory() as d:
            f=Fake();b=ct.Bridge(f,d,max_calls=1)
            self.assertIn('attractions_keys',b([{'role':'user','content':'原句'}]))
            self.assertIn('原句',f.seen[1])
            self.assertTrue((Path(d)/'call_001.json').exists())
            with self.assertRaises(ct.BudgetStop):b([])

    def test_invalid_response_stops(self):
        class Fake:
            telemetry=[]
            def complete(self,*a):return '我没有工具。'
        with tempfile.TemporaryDirectory() as d:
            b=ct.Bridge(Fake(),d)
            b([])
            with self.assertRaises(ct.BudgetStop):b([])
            self.assertEqual(b.calls,2)

    def test_official_schema_rejects_old_arrays(self):
        import jsonschema
        schema=ct.read(ct.UPSTREAM/'chinatravel/evaluation/output_schema.json')
        self.assertFalse(jsonschema.Draft7Validator(schema).is_valid([]))
        self.assertFalse(jsonschema.Draft7Validator(schema).is_valid([[{'days':1}]]))

class OfficialScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture=ct.read(ROOT/'docs/experiments/chinatravel_setup/codex_validation/fixture_candidate.json')
        cls.query=fixture['query']; cls.plan=fixture['result']
        # Fixture generated offline WITH gold for evaluator validation only.
        # Never use this plan or its query as an agent demonstration.

    def score(self,q,p):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return ct.evaluate(q,p)

    def test_known_valid_fixture(self):
        s=self.score({'positive':self.query},{'positive':self.plan})
        self.assertEqual(s['all_pass_rate'],100,s)

    def test_missing_prediction_stays_in_denominator(self):
        s=self.score({'positive':self.query,'missing':self.query},{'positive':self.plan})
        self.assertEqual(s['n_expected'],2)
        self.assertEqual(s['all_pass_rate'],50)
        self.assertEqual(s['schema_rate'],50)

    def test_empty_fails(self):
        s=self.score({'empty':self.query},{'empty':{}})
        self.assertEqual(s['all_pass_rate'],0)
        self.assertEqual(s['schema_rate'],0)

    def test_hard_constraint_failure(self):
        q=copy.deepcopy(self.query);q['hard_logic_py']=['result = False']
        s=self.score({'hard':q},{'hard':self.plan})
        self.assertEqual(s['schema_rate'],100)
        self.assertEqual(s['commonsense_macro'],100)
        self.assertEqual(s['hard_macro'],0)
        self.assertEqual(s['all_pass_rate'],0)

    def test_invalid_entity(self):
        p=copy.deepcopy(self.plan)
        a=next(a for day in p['itinerary'] for a in day['activities'] if 'position' in a)
        a['position']='NONEXISTENT_SENTINEL_POI'
        s=self.score({'entity':self.query},{'entity':p})
        self.assertEqual(s['schema_rate'],100)
        self.assertEqual(s['commonsense_macro'],0)

    def test_time_conflict(self):
        p=copy.deepcopy(self.plan)
        a=p['itinerary'][0]['activities'][0]
        a['start_time']='23:59';a['end_time']='00:00'
        s=self.score({'time':self.query},{'time':p})
        self.assertEqual(s['schema_rate'],100)
        self.assertEqual(s['commonsense_macro'],0)

    def test_unexpected_id_rejected(self):
        with self.assertRaises(ValueError):self.score({'a':self.query},{'extra':{}})

if __name__ == '__main__':unittest.main()
