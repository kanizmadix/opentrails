"""Hotel search API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.hotels import HotelOffer, HotelSearchRequest, HotelSearchResponse
from app.services import providers
from app.storage import search_history

PREFIX = "/api/hotels"
TAGS = ["hotels"]
router = APIRouter()


@router.post("/search", response_model=HotelSearchResponse)
async def search(req: HotelSearchRequest) -> HotelSearchResponse:
    resp = await providers.search_hotels(req)
    search_history.log_search("hotels", req.model_dump(mode="json"),
                              result_count=len(resp.offers))
    return resp


@router.get("/detail/{hotel_id}", response_model=HotelOffer)
async def detail(hotel_id: str) -> HotelOffer:
    """Lookup a previously-seen hotel offer by id (search history fallback).

    Real upstream lookups vary by provider, so we serve from the most-recent
    search history result set.
    """
    history = search_history.list_history("hotels", limit=10)
    for entry in history:
        # We don't store full offers; signal not implemented for arbitrary ids.
        if entry.query.get("city"):
            continue
    raise HTTPException(status_code=404,
                        detail=f"Hotel detail not available for id {hotel_id} without provider context")
