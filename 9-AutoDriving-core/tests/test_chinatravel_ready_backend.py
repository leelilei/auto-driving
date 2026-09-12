import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pandas as pd
from chinatravel_ready_backend import ConstraintAwareAgent,requirements

class ReadyTests(unittest.TestCase):
 def agent(self,**intent):
  agent=object.__new__(ConstraintAwareAgent);agent.intent=intent;return agent
 def test_missing_people_is_clarification_not_default(self):
  q=dict(start_city='深圳',target_city='广州',days=2,people_number=None)
  self.assertEqual(requirements(q)['status'],'NEEDS_CLARIFICATION')
  self.assertIsNone(q['people_number'])
 def test_explicit_hooks(self):
  a=self.agent(budget=5600,room_count=2,room_type=2)
  self.assertEqual(a.extract_budget({}),5600);self.assertEqual(a.decide_rooms({}),(2,2))
  self.assertIsNone(self.agent(budget=None).extract_budget({}))
 def test_transport_filter_and_price_order(self):
  f=pd.DataFrame([dict(TrainID='A',FlightID=None,Cost=800,Duration=5,BeginTime='06:00'),dict(TrainID=None,FlightID='F',Cost=100,Duration=1,BeginTime='08:00'),dict(TrainID='B',FlightID=None,Cost=200,Duration=7,BeginTime='07:00')])
  self.assertEqual(self.agent(intercity_mode='train').ranking_intercity_transport_go(f,{}),[2,0])
 def test_hotel_positions_not_ids(self):
  f=pd.DataFrame([dict(id=70,numbed=1,price=50),dict(id=90,numbed=2,price=120),dict(id=110,numbed=2,price=80)])
  self.assertEqual(self.agent(room_type=2).ranking_hotel(f,{}),[2,1])
if __name__=='__main__':unittest.main()
