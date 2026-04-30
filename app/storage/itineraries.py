"""Itinerary persistence (one row per day-plan, JSON serialized)."""
from __future__ import annotations

import json
from typing import List

from app.db import cursor
from app.models.itinerary import DayPlan, ItineraryResponse


def save_itinerary(trip_id: int, itinerary: ItineraryResponse) -> List[int]:
    """Persist all day-plans for a given trip. Returns inserted row ids."""
    inserted: List[int] = []
    with cursor() as cur:
        # delete prior plans for this trip
        cur.execute("DELETE FROM itineraries WHERE trip_id = ?", (trip_id,))
        for day_plan in itinerary.days:
            cur.execute(
                """INSERT INTO itineraries (trip_id, day, title, plan_json)
                   VALUES (?, ?, ?, ?)""",
                (trip_id, day_plan.day, day_plan.title, day_plan.model_dump_json()),
            )
            inserted.append(cur.lastrowid)
    return inserted


def list_for_trip(trip_id: int) -> List[DayPlan]:
    with cursor() as cur:
        cur.execute(
            "SELECT plan_json FROM itineraries WHERE trip_id = ? ORDER BY day ASC",
            (trip_id,),
        )
        rows = cur.fetchall()
    plans: List[DayPlan] = []
    for r in rows:
        try:
            plans.append(DayPlan.model_validate(json.loads(r["plan_json"])))
        except Exception:
            continue
    return plans


def delete_for_trip(trip_id: int) -> int:
    with cursor() as cur:
        cur.execute("DELETE FROM itineraries WHERE trip_id = ?", (trip_id,))
        return cur.rowcount
