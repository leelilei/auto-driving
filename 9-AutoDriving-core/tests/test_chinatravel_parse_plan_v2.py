from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'9-AutoDriving-core/scripts'))
import chinatravel_parse_plan_v2 as p


class RoutingTests(unittest.TestCase):
    def parsed(self,requirements):
        return {'start_city':'上海','target_city':'杭州','days':1,'people_number':1,'budget':1500,'unsupported_requirements':requirements}

    def test_generic_output_request_is_fulfilled_by_planner(self):
        original='当前位置上海。请给我一个旅行规划。'
        raw=self.parsed(['请给我一个旅行规划（具体行程规划）'])
        result=p.route(raw,original)
        self.assertEqual(result['unresolved_requirements'],[])
        self.assertEqual(len(result['resolved_by_planner']),1)
        self.assertEqual(raw['unsupported_requirements'],['请给我一个旅行规划（具体行程规划）'])

    def test_specific_constraints_and_ungrounded_requests_are_not_removed(self):
        for requirement in ['请给我一个旅行规划，不坐飞机','请给我一个旅行规划（不要特种兵出行）',
                            '不要特种兵出行','想吃火锅','预算1000元','每天最多两个景点','请给我一份行程安排']:
            with self.subTest(requirement=requirement):
                result=p.route(self.parsed([requirement]),'请给我一个旅行规划。')
                self.assertEqual(result['unresolved_requirements'],[requirement])
                self.assertEqual(result['resolved_by_planner'],[])


if __name__=='__main__':unittest.main()
