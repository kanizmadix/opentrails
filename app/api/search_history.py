"""Search history API."""
from __future__ import annotations

from fastapi import APIRouter, status

from app.models.trips import SearchHistoryItem
from app.storage import search_history as history_storage

PREFIX = "/api/search-history"
TAGS = ["search-history"]
router = APIRouter()


@router.get("", response_model=list[SearchHistoryItem])
async def list_(limit: int = 50) -> list[SearchHistoryItem]:
    return history_storage.list_history(limit=limit)


@router.get("/{domain}", response_model=list[SearchHistoryItem])
async def by_domain(domain: str, limit: int = 50) -> list[SearchHistoryItem]:
    return history_storage.list_history(domain=domain, limit=limit)


@router.delete("/{domain}", status_code=status.HTTP_204_NO_CONTENT)
async def clear(domain: str) -> None:
    history_storage.clear_domain(domain)
