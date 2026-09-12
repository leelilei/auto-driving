"""Minimal ChinaTravel plan schema adapter with an explicit change log."""
import copy


def adapt(plan):
    """Coerce only documented room_type numeric strings; invent no values."""
    result = copy.deepcopy(plan)
    changes = []
    for day_index, day in enumerate(result.get('itinerary', [])):
        for activity_index, activity in enumerate(day.get('activities', [])):
            value = activity.get('room_type')
            if activity.get('type') == 'accommodation' and value in ('1', '2'):
                activity['room_type'] = int(value)
                changes.append({
                    'path': f'itinerary/{day_index}/activities/{activity_index}/room_type',
                    'before': value,
                    'after': int(value),
                    'rule': 'accommodation room_type numeric-string to integer',
                })
    return result, changes
