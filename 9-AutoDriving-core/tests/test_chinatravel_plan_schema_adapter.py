import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '9-AutoDriving-core/scripts'))
from chinatravel_plan_schema_adapter import adapt


class AdapterTests(unittest.TestCase):
    def test_only_accommodation_room_type_is_coerced(self):
        raw = {'itinerary': [{'activities': [
            {'type': 'accommodation', 'room_type': '2'},
            {'type': 'accommodation', 'room_type': 'unknown'},
            {'type': 'attraction', 'room_type': '2'},
        ]}]}
        frozen = copy.deepcopy(raw)
        result, changes = adapt(raw)
        self.assertEqual(raw, frozen)
        self.assertEqual(result['itinerary'][0]['activities'][0]['room_type'], 2)
        self.assertEqual(result['itinerary'][0]['activities'][1]['room_type'], 'unknown')
        self.assertEqual(result['itinerary'][0]['activities'][2]['room_type'], '2')
        self.assertEqual(len(changes), 1)

    def test_missing_structure_is_not_filled(self):
        self.assertEqual(adapt({}), ({}, []))


if __name__ == '__main__':
    unittest.main()
