# OpenTrails

> An open-API travel platform — flights, hotels, attractions, AI itineraries — built on **100% open data** + **Claude `claude-sonnet-4-6`**, with an Apple-aesthetic frontend.

Built to compete with closed travel platforms (GT Holidays, Booking, etc.) using only open APIs and open standards.

## What's inside

| Domain | Open API |
|--------|----------|
| Maps & geocoding | OpenStreetMap + Nominatim + Leaflet |
| Tourist attractions | OpenTripMap + OSM Overpass |
| Weather | Open-Meteo |
| Country / visa info | REST Countries |
| Currency | Frankfurter (ECB) |
| Destination guides | Wikipedia + Wikivoyage REST |
| Flights | Amadeus Self-Service + Kiwi Tequila (free tiers) |
| Hotels | Amadeus Hotel Search + OSM/OpenTripMap |
| AI itinerary, packing, translator, intel | Claude `claude-sonnet-4-6` |

## Quick start

```bash
git clone https://github.com/kanizmadix/opentrails.git
cd opentrails
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000
```

## Project layout

```
opentrails/
├── app/
│   ├── main.py            # FastAPI entrypoint + auto router discovery
│   ├── config.py          # pydantic-settings
│   ├── logger.py          # structured JSON logging
│   ├── db.py              # SQLite + schema
│   ├── exceptions.py      # domain errors + handlers
│   ├── rate_limiter.py    # per-IP token bucket
│   ├── api/               # FastAPI routers (auto-registered)
│   ├── services/          # External API integrations
│   ├── ai/                # Claude-powered features
│   ├── models/            # Pydantic request/response models
│   ├── storage/           # SQLite persistence layer
│   └── utils/             # http, cache helpers
├── frontend/
│   ├── templates/         # Jinja2 (Apple-aesthetic)
│   └── static/            # CSS, JS, images, Leaflet maps
├── tests/
├── data/                  # SQLite DB lives here
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── .github/workflows/ci.yml
```

More features and full API docs added in subsequent commits.
