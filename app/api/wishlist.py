"""Wishlist API."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, status

from app.models.trips import WishlistItem
from app.storage import wishlist as wishlist_storage

PREFIX = "/api/wishlist"
TAGS = ["wishlist"]
router = APIRouter()


@router.post("", response_model=WishlistItem, status_code=status.HTTP_201_CREATED)
async def add(item: WishlistItem) -> WishlistItem:
    return wishlist_storage.add_to_wishlist(item)


@router.get("", response_model=List[WishlistItem])
async def list_(kind: Optional[str] = None, limit: int = 100) -> List[WishlistItem]:
    return wishlist_storage.list_wishlist(kind=kind, limit=limit)


@router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(wishlist_id: int) -> None:
    wishlist_storage.remove_from_wishlist(wishlist_id)
