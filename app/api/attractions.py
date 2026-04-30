"""Attractions API."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.attractions import (
    AttractionCategory,
    AttractionDetail,
    AttractionSearchRequest,
    AttractionsResponse,
)
from app.services import opentripmap, providers
from app.storage import search_history

PREFIX = "/api/attractions"
TAGS = ["attractions"]
router = APIRouter()


@router.get("/search", response_model=AttractionsResponse)
async def search(lat: float = Query(..., ge=-90, le=90),
                 lon: float = Query(..., ge=-180, le=180),
                 radius_m: int = Query(2000, ge=100, le=50000),
                 kinds: str = Query("", description="comma-separated category names"),
                 limit: int = Query(30, ge=1, le=200)) -> AttractionsResponse:
    kinds_list = [k.strip() for k in kinds.split(",") if k.strip()] or None
    items, provider = await providers.search_attractions(
        lat=lat, lon=lon, radius_m=radius_m, kinds=kinds_list, limit=limit,
    )
    request = AttractionSearchRequest(
        lat=lat, lon=lon, radius_m=radius_m,
        kinds=[AttractionCategory(k) for k in (kinds_list or []) if k in AttractionCategory.__members__.values()
               or k in [c.value for c in AttractionCategory]],
        limit=limit,
    )
    search_history.log_search("attractions", request.model_dump(mode="json"),
                              result_count=len(items))
    return AttractionsResponse(request=request, items=items,
                               provider=provider, count=len(items))


@router.get("/detail/{xid}", response_model=AttractionDetail)
async def detail(xid: str) -> AttractionDetail:
    return await opentripmap.poi_detail(xid)


@router.get("/categories", response_model=list[str])
async def categories() -> list[str]:
    return [c.value for c in AttractionCategory]
