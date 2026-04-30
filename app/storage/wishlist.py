"""Wishlist persistence."""
from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from app.db import cursor
from app.exceptions import NotFoundError
from app.models.trips import WishlistItem


def _row_to_item(row) -> WishlistItem:
    created = row["created_at"]
    try:
        created_dt = datetime.fromisoformat(created) if created else None
    except ValueError:
        created_dt = None
    return WishlistItem(
        id=row["id"],
        kind=row["kind"],
        payload=json.loads(row["payload_json"]),
        notes=row["notes"],
        created_at=created_dt,
    )


def add_to_wishlist(item: WishlistItem) -> WishlistItem:
    with cursor() as cur:
        cur.execute(
            "INSERT INTO wishlist (kind, payload_json, notes) VALUES (?, ?, ?)",
            (item.kind, json.dumps(item.payload), item.notes),
        )
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM wishlist WHERE id = ?", (new_id,))
        row = cur.fetchone()
    return _row_to_item(row)


def list_wishlist(kind: Optional[str] = None, limit: int = 100) -> List[WishlistItem]:
    with cursor() as cur:
        if kind:
            cur.execute(
                "SELECT * FROM wishlist WHERE kind = ? ORDER BY created_at DESC LIMIT ?",
                (kind, limit),
            )
        else:
            cur.execute(
                "SELECT * FROM wishlist ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = cur.fetchall()
    return [_row_to_item(r) for r in rows]


def remove_from_wishlist(wishlist_id: int) -> None:
    with cursor() as cur:
        cur.execute("DELETE FROM wishlist WHERE id = ?", (wishlist_id,))
        if cur.rowcount == 0:
            raise NotFoundError(f"Wishlist item {wishlist_id} not found")
