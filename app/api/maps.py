"""Maps and geocoding API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.common import Place
from app.services import nominatim, overpass

PREFIX = "/api/maps"
TAGS = ["maps"]
router = APIRouter()


@router.get("/geocode", response_model=list[Place])
async def geocode(q: str = Query(..., min_length=1),
                  limit: int = Query(5, ge=1, le=20)) -> list[Place]:
    return await nominatim.geocode(q, limit=limit)


@router.get("/reverse", response_model=Place | None)
async def reverse(lat: float = Query(..., ge=-90, le=90),
                  lon: float = Query(..., ge=-180, le=180)) -> Place | None:
    place = await nominatim.reverse(lat, lon)
    if not place:
        raise HTTPException(status_code=404, detail="No location found")
    return place


@router.get("/pois")
async def pois(bbox: str = Query(..., description="south,west,north,east"),
               kinds: str = Query("tourism")) -> list:
    parts = [float(x) for x in bbox.split(",")]
    if len(parts) != 4:
        raise HTTPException(status_code=400, detail="bbox must be 'south,west,north,east'")
    cats = [k.strip() for k in kinds.split(",") if k.strip()]
    return await overpass.query_pois(tuple(parts), cats)
