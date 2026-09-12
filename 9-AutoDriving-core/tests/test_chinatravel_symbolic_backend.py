import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_symbolic_backend as backend
ct=backend.ct


class BackendTests(unittest.TestCase):
    def test_duplicate_meal_is_not_selected_again(self):
        agent=object.__new__(backend.MealStateRuleAgent)
        agent.query={'days':1}
        poi={'back_transport':{'BeginTime':'23:00'}}
        for meal,at in [('lunch','12:00'),('dinner','18:00')]:
            with self.subTest(meal=meal):
                selected,_=agent.select_next_poi_type([], [{'activities':[]}],poi,0,at,'point')
                self.assertEqual(selected,meal)
                selected,candidates=agent.select_next_poi_type([], [{'activities':[{'type':meal}]}],poi,0,at,'point')
                self.assertNotEqual(selected,meal)
                self.assertNotIn(meal,candidates)

    def test_gold_and_arbitrary_expression_rejected(self):
        intent={'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':1500}
        with self.assertRaises(ValueError):backend.compile_intent(dict(intent,hard_logic_py=['result=True']))
        with self.assertRaises(ValueError):backend.compile_intent(dict(intent,budget='__import__("os")'))

    def test_compiled_budget_constraint_changes_result(self):
        from chinatravel.symbol_verification.hard_constraint import evaluate_constraints_py
        intent={'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':100}
        plan={'people_number':1,'start_city':'上海','target_city':'杭州','itinerary':[{'day':1,'activities':[{'cost':80,'transports':[{'cost':30}]}]}]}
        self.assertEqual(list(map(bool,evaluate_constraints_py(backend.compile_intent(intent),plan))),[True,True,False])
        self.assertEqual(list(map(bool,evaluate_constraints_py(backend.compile_intent(dict(intent,budget=110)),plan))),[True,True,True])

    def test_real_search_with_unchanged_official_evaluator(self):
        intent={'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':1500}
        with tempfile.TemporaryDirectory() as temp:
            prediction,summary=backend.solve(intent,Path(temp)/'search')
            self.assertTrue(summary['search_success'],summary)
            self.assertTrue(summary['schema_valid'])
            self.assertGreater(summary['tool_calls'],0)
            query={**intent,'uid':'test','hard_logic_py':backend.compile_intent(intent)}
            with ct.offline(),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                score=ct.v1.evaluate({'test':query},{'test':prediction})
            self.assertEqual(score['all_pass_rate'],100,score)
            for day in prediction['itinerary']:
                self.assertLessEqual(sum(a['type']=='lunch' for a in day['activities']),1)


if __name__=='__main__':unittest.main()
