"""Trip CRUD persistence on SQLite."""
from __future__ import annotations

from datetime import date, datetime

from app.db import cursor
from app.exceptions import NotFoundError
from app.models.trips import TripCreate, TripRecord, TripUpdate


def _row_to_record(row) -> TripRecord:
    def _date(v: str | None) -> date | None:
        return date.fromisoformat(v) if v else None

    def _dt(v: str | None) -> datetime | None:
        if not v:
            return None
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    return TripRecord(
        id=row["id"],
        name=row["name"],
        origin=row["origin"],
        destination=row["destination"],
        start_date=_date(row["start_date"]),
        end_date=_date(row["end_date"]),
        travelers=row["travelers"] or 1,
        budget_usd=row["budget_usd"],
        notes=row["notes"],
        created_at=_dt(row["created_at"]),
        updated_at=_dt(row["updated_at"]),
    )


def create_trip(payload: TripCreate) -> TripRecord:
    with cursor() as cur:
        cur.execute(
            """INSERT INTO trips (name, origin, destination, start_date, end_date,
                                  travelers, budget_usd, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                payload.name, payload.origin, payload.destination,
                payload.start_date.isoformat() if payload.start_date else None,
                payload.end_date.isoformat() if payload.end_date else None,
                payload.travelers, payload.budget_usd, payload.notes,
            ),
        )
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM trips WHERE id = ?", (new_id,))
        row = cur.fetchone()
    return _row_to_record(row)


def list_trips(limit: int = 50, offset: int = 0) -> list[TripRecord]:
    with cursor() as cur:
        cur.execute(
            "SELECT * FROM trips ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = cur.fetchall()
    return [_row_to_record(r) for r in rows]


def get_trip(trip_id: int) -> TripRecord:
    with cursor() as cur:
        cur.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
    if not row:
        raise NotFoundError(f"Trip {trip_id} not found")
    return _row_to_record(row)


def update_trip(trip_id: int, payload: TripUpdate) -> TripRecord:
    fields = payload.model_dump(exclude_none=True)
    if not fields:
        return get_trip(trip_id)
    set_clauses = []
    values: list = []
    for k, v in fields.items():
        if isinstance(v, date):
            v = v.isoformat()
        set_clauses.append(f"{k} = ?")
        values.append(v)
    set_clauses.append("updated_at = datetime('now')")
    values.append(trip_id)
    with cursor() as cur:
        cur.execute(f"UPDATE trips SET {', '.join(set_clauses)} WHERE id = ?", values)
        if cur.rowcount == 0:
            raise NotFoundError(f"Trip {trip_id} not found")
        cur.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
    return _row_to_record(row)


def delete_trip(trip_id: int) -> None:
    with cursor() as cur:
        cur.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        if cur.rowcount == 0:
            raise NotFoundError(f"Trip {trip_id} not found")
