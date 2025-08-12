from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict


def generate_weekly_schedule(tasks: List[Dict], staff_ids: List[int], start_monday: datetime) -> List[Dict]:
    """Greedy weekly scheduler. Distributes tasks across staff and days.

    tasks: list of {request_id, priority}
    staff_ids: list of available staff ids
    start_monday: week start date (Monday)
    """
    tasks_sorted = sorted(tasks, key=lambda t: t.get("priority", 3))
    schedule: List[Dict] = []
    day_slots = [start_monday + timedelta(days=i) for i in range(7)]

    if not staff_ids:
        return schedule

    staff_index = 0
    day_index = 0
    for task in tasks_sorted:
        scheduled_for = day_slots[day_index]
        staff_id = staff_ids[staff_index]
        schedule.append({
            "request_id": task["request_id"],
            "staff_id": staff_id,
            "scheduled_for": scheduled_for,
        })
        # round-robin
        staff_index = (staff_index + 1) % len(staff_ids)
        if staff_index == 0:
            day_index = (day_index + 1) % len(day_slots)

    return schedule