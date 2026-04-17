"""Tests for wishlist storage."""
from __future__ import annotations

import pytest

from app.exceptions import NotFoundError
from app.models.trips import WishlistItem
from app.storage import wishlist as wishlist_storage


def test_add_and_list_wishlist():
    a = wishlist_storage.add_to_wishlist(WishlistItem(
        kind="destination", payload={"name": "Kyoto"}, notes="Cherry blossom",
    ))
    b = wishlist_storage.add_to_wishlist(WishlistItem(
        kind="hotel", payload={"name": "Park Hotel"},
    ))
    items = wishlist_storage.list_wishlist()
    ids = {x.id for x in items}
    assert a.id in ids and b.id in ids


def test_filter_by_kind():
    wishlist_storage.add_to_wishlist(WishlistItem(kind="destination", payload={"name": "X"}))
    wishlist_storage.add_to_wishlist(WishlistItem(kind="flight", payload={"id": "f1"}))
    only_flights = wishlist_storage.list_wishlist(kind="flight")
    assert all(x.kind == "flight" for x in only_flights)


def test_remove_then_404():
    item = wishlist_storage.add_to_wishlist(WishlistItem(kind="hotel", payload={}))
    wishlist_storage.remove_from_wishlist(item.id)
    with pytest.raises(NotFoundError):
        wishlist_storage.remove_from_wishlist(item.id)
