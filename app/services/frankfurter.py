"""Frankfurter currency conversion client (ECB rates, free, no key)."""
from __future__ import annotations

from datetime import date

from app.config import settings
from app.logger import get_logger
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60 * 6  # 6h


async def convert(from_ccy: str, to_ccy: str, *, amount: float = 1.0,
                  on_date: date | None = None) -> dict[str, float]:
    """Return {amount, rate, from, to, date}."""
    from_ccy = from_ccy.upper()
    to_ccy = to_ccy.upper()
    if from_ccy == to_ccy:
        return {"amount": amount, "rate": 1.0, "from": from_ccy, "to": to_ccy,
                "date": (on_date or date.today()).isoformat()}
    date_path = on_date.isoformat() if on_date else "latest"
    key = f"frankfurter:{date_path}:{from_ccy}:{to_ccy}:{amount}"

    async def _fetch() -> dict:
        url = f"{settings.FRANKFURTER_BASE}/{date_path}"
        params = {"from": from_ccy, "to": to_ccy, "amount": amount}
        return await get_json(url, params=params)

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    rates = raw.get("rates") or {}
    converted = float(rates.get(to_ccy, 0.0))
    rate = converted / amount if amount else 0.0
    return {
        "amount": converted,
        "rate": rate,
        "from": from_ccy,
        "to": to_ccy,
        "date": raw.get("date") or date_path,
    }


async def latest_rates(base: str = "USD") -> dict[str, float]:
    """Get latest ECB rates with given base."""
    base = base.upper()
    key = f"frankfurter:latest:{base}"

    async def _fetch() -> dict:
        url = f"{settings.FRANKFURTER_BASE}/latest"
        return await get_json(url, params={"from": base})

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    return {k: float(v) for k, v in (raw.get("rates") or {}).items()}
