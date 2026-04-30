"""Search history persistence."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.db import cursor
from app.models.trips import SearchHistoryItem


def _row_to_item(row) -> SearchHistoryItem:
    created = row["created_at"]
    try:
        created_dt = datetime.fromisoformat(created) if created else None
    except ValueError:
        created_dt = None
    return SearchHistoryItem(
        id=row["id"],
        domain=row["domain"],
        query=json.loads(row["query_json"]),
        result_count=row["result_count"],
        duration_ms=row["duration_ms"],
        created_at=created_dt,
    )


def log_search(domain: str, query: dict[str, Any], *,
               result_count: int | None = None,
               duration_ms: int | None = None) -> SearchHistoryItem:
    with cursor() as cur:
        cur.execute(
            """INSERT INTO search_history (domain, query_json, result_count, duration_ms)
               VALUES (?, ?, ?, ?)""",
            (domain, json.dumps(query, default=str), result_count, duration_ms),
        )
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM search_history WHERE id = ?", (new_id,))
        row = cur.fetchone()
    return _row_to_item(row)


def list_history(domain: str | None = None, limit: int = 50) -> list[SearchHistoryItem]:
    with cursor() as cur:
        if domain:
            cur.execute(
                "SELECT * FROM search_history WHERE domain = ? ORDER BY created_at DESC LIMIT ?",
                (domain, limit),
            )
        else:
            cur.execute(
                "SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = cur.fetchall()
    return [_row_to_item(r) for r in rows]


def clear_domain(domain: str) -> int:
    with cursor() as cur:
        cur.execute("DELETE FROM search_history WHERE domain = ?", (domain,))
        return cur.rowcount
