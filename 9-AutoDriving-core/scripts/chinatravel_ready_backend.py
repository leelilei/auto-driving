"""Constraint-aware local RuleNeSy adapter; no gold, model calls, or plan repair."""
import math
from chinatravel_symbolic_backend import MealStateRuleAgent


def requirements(intent):
    missing=[k for k in ('start_city','target_city','days','people_number') if intent.get(k) is None]
    return {'status':'NEEDS_CLARIFICATION' if missing else 'READY_TO_PLAN',
            'missing_fields':missing,
            'question':'请明确出行人数。' if missing==['people_number'] else ('请补充：'+', '.join(missing) if missing else None)}


class ConstraintAwareAgent(MealStateRuleAgent):
    def __init__(self, *, intent, **kwargs):
        self.intent=dict(intent)
        super().__init__(**kwargs)

    def decide_rooms(self, query):
        return self.intent.get('room_count'),self.intent.get('room_type')

    def extract_budget(self, query):
        return self.intent.get('budget')

    def _transport_indices(self, frame, returning=False):
        mode=self.intent.get('intercity_mode')
        def present(value):
            import pandas as pd
            return value is not None and not pd.isna(value)
        ids=[i for i in range(len(frame)) if mode is None or present(frame.iloc[i].get('TrainID' if mode=='train' else 'FlightID'))]
        # Row positions, not identifiers or an argsort array treated as ranks.
        return sorted(ids,key=lambda i:(float(frame.iloc[i]['Cost']),float(frame.iloc[i]['Duration']),str(frame.iloc[i]['BeginTime'])))

    def ranking_intercity_transport_go(self, frame, query):
        return self._transport_indices(frame)

    def ranking_intercity_transport_back(self, frame, query, selected_go):
        return self._transport_indices(frame,True)

    def ranking_hotel(self, frame, query):
        rt=self.intent.get('room_type')
        ids=[i for i in range(len(frame)) if rt is None or int(frame.iloc[i]['numbed'])==rt]
        return sorted(ids,key=lambda i:(float(frame.iloc[i]['price']),i))
