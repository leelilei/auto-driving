import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import chinatravel_parse_plan_v4 as p

class V4Tests(unittest.TestCase):
 def test_unspecified_budget_is_null_and_evidence_preserved(self):
    r = p.parse('[当前位置北京,目标位置重庆,旅行人数2,旅行天数5] 重庆应该怎么玩')
    assert r['budget'] is None and r['evidence']['budget'] == ''
    assert r['days'] == 5 and r['evidence']['target_city'] == '重庆'

 def test_explicit_fields_and_unsupported_are_retained(self):
    r = p.parse('当前位置深圳。我打算去广州玩两天，预算1000元，想吃火锅，开一间单床房。')
    assert r['budget'] == 1000 and '想吃火锅' in r['unsupported_requirements']
    assert '开一间单床房' in r['unsupported_requirements']

 def test_extended_compiler_adds_only_resolved_constraints(self):
    r = p.parse('当前位置深圳。我打算去广州玩两天，预算1000元。')
    r.update(room_count=1, room_type=1, intercity_mode='train')
    clauses = p.compile_extended(r)
    assert len(clauses) == 6
    assert 'room_count' in clauses[3] and 'room_type' in clauses[4]
    assert 'intercity_transport_type' in clauses[5]

 def test_missing_required_field_rejected(self):
    r = p.parse('[当前位置北京,目标位置重庆,旅行人数2,旅行天数5] 重庆应该怎么玩')
    r['days'] = None
    with self.assertRaises(ValueError): p.compile_intent(r)

if __name__ == '__main__': unittest.main()
