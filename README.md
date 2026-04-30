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

## API reference

All routes are versioned under `/api/*`. Open `http://localhost:8000/docs` for interactive Swagger UI.

### Health
- `GET /api/health` — liveness + Claude key presence

### Maps & geocoding
- `GET /api/maps/geocode?q=...` — Nominatim search
- `GET /api/maps/reverse?lat=..&lon=..` — reverse geocode
- `GET /api/maps/pois?bbox=s,w,n,e&kinds=tourism,historic` — Overpass POIs

### Destinations
- `GET /api/destinations/search?q=...` — text search
- `GET /api/destinations/{country_code}/intel` — full destination intel (Claude-synthesized)
- `GET /api/destinations/weather?lat=..&lon=..&days=7` — Open-Meteo forecast
- `GET /api/destinations/currency?from=USD&to=EUR&amount=100` — Frankfurter conversion

### Flights
- `POST /api/flights/search` — multi-provider flight offers
- `GET /api/flights/fare-calendar?origin=&destination=&start_date=&days=` — cheapest fare per day

### Hotels
- `POST /api/hotels/search`
- `GET /api/hotels/detail/{hotel_id}`

### Attractions
- `GET /api/attractions/search?lat=&lon=&radius_m=&kinds=&limit=`
- `GET /api/attractions/detail/{xid}`
- `GET /api/attractions/categories`

### Itinerary
- `POST /api/itinerary/generate` — Claude builds day-by-day plan
- `POST /api/itinerary/save?trip_id=...` — persist to DB
- `GET /api/itinerary/trip/{trip_id}` — saved plan

### Trips (CRUD)
- `POST /api/trips`, `GET /api/trips`, `GET /api/trips/{id}`,
  `PATCH /api/trips/{id}`, `DELETE /api/trips/{id}`

### Wishlist
- `POST /api/wishlist`, `GET /api/wishlist?kind=...`, `DELETE /api/wishlist/{id}`

### Translator
- `POST /api/translator/phrasebook` — generate 30+ travel phrases via Claude
- `POST /api/translator/translate` — single phrase

### Packing
- `POST /api/packing/generate` — destination + dates + activities -> categorized list

### Search history
- `GET /api/search-history`, `GET /api/search-history/{domain}`,
  `DELETE /api/search-history/{domain}`

## Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | yes | — | Claude API key (`claude-sonnet-4-6` with prompt caching) |
| `CLAUDE_MODEL` | no | `claude-sonnet-4-6` | Override model id |
| `CLAUDE_MAX_TOKENS` | no | `2048` | Per-call default |
| `AMADEUS_CLIENT_ID` / `AMADEUS_CLIENT_SECRET` | no | — | Real flight + hotel offers |
| `KIWI_API_KEY` | no | — | Kiwi Tequila flight fallback |
| `OPENTRIPMAP_API_KEY` | no | — | Higher-quality POI data |
| `DATABASE_URL` | no | `sqlite:///./data/opentrails.db` | SQLite path |
| `LOG_LEVEL` | no | `INFO` | Log verbosity |
| `RATE_LIMIT_PER_MINUTE` | no | `120` | Per-IP cap |
| `CACHE_TTL_SECONDS` | no | `900` | Default upstream cache TTL |
| `CORS_ORIGINS` | no | `*` | Comma-separated allowlist |

Without provider keys, the API returns clearly-tagged `provider: "mock"` payloads so the
frontend remains usable in dev mode.

## Testing

```bash
make install
make test    # pytest -q (mocks all upstream HTTP via respx)
make lint    # ruff check .
```

The CI workflow at `.github/workflows/ci.yml` runs the same on every push / PR.

## Deployment

### Docker

```bash
make docker-build
make docker-run
# or:
docker compose up -d
```

The image runs on Python 3.11-slim as a non-root `app` user, exposes port 8000,
and includes a `/api/health` HTTP healthcheck. The SQLite DB lives in the
`/app/data` volume.

### Bare metal

```bash
make install
make init-db
make dev   # uvicorn with --reload
```

Behind a reverse proxy (Nginx / Caddy), terminate TLS at the proxy and forward
`/` and `/api/*` to `127.0.0.1:8000`.

## Frontend

OpenTrails ships with an Apple-aesthetic frontend served from `frontend/`. It is
**vanilla** — no build step, no framework — designed to be readable, accessible,
and theme-aware on first paint.

### Design system

Tokens live in `frontend/static/css/tokens.css` and define:

- **Color** — light (`#fbfbfd` / `#1d1d1f`) and dark (`#000` / `#f5f5f7`) palettes
  with shared Apple-blue accent (`#0071e3` light, `#2997ff` dark).
- **Typography** — SF Pro fallback chain, fluid `clamp()` sizes from 13px caption
  to 96px display, tight letter-spacing for large heads.
- **Spacing** — 4px-base, 8px grid (`--space-1` through `--space-44` / 180px).
- **Radii** — 6 / 10 / 14 / 18 / 22 / 28 px, plus pill `980px`.
- **Shadows / motion** — soft elevation shadows; `cubic-bezier(0.16, 1, 0.3, 1)`
  ease-out for the Apple "snap".

### File map

```
frontend/
├── templates/                  # Jinja2 — extend base.html
│   ├── base.html               # head, theme bootstrap, asset links
│   ├── home.html               # hero · discover · spotlight · plan · CTA
│   ├── search.html             # global search w/ tabs
│   ├── flights.html            # flight search + filters + fare calendar
│   ├── hotels.html             # split list/map view
│   ├── attractions.html        # category chips + map + cards
│   ├── destination.html        # hero · intel · weather · currency · sights
│   ├── itinerary.html          # AI itinerary form + day timeline
│   ├── trip.html               # saved trips grid
│   ├── wishlist.html
│   ├── about.html              # mission + open-data manifesto + sources
│   └── components/             # nav, footer, skeleton macros
└── static/
    ├── css/
    │   ├── tokens.css          # design tokens (light + dark)
    │   ├── reset.css base.css typography.css layout.css animations.css
    │   ├── components/         # buttons, cards, nav, forms, badges,
    │   │                       # dialog, footer, map, timeline
    │   └── pages/              # home, search, flights, hotels,
    │                           # destination, itinerary, trip, about
    ├── js/
    │   ├── api.js              # fetch helper (window.api / window.tryApi)
    │   ├── theme.js            # light/dark/system + persistence
    │   ├── nav.js reveal.js leaflet-map.js
    │   ├── components/         # toast, dialog, datepicker, search-bar,
    │   │                       # carousel, skeleton
    │   └── pages/              # one module per template
    └── img/                    # logo.svg, favicon.svg, og-image.svg
```

### Theming

Theme is bootstrapped inline in `<head>` (no FOUC) and stored in
`localStorage["opentrails:theme"]` as `"light"` | `"dark"` | unset (system).
Every `data-theme-toggle` button cycles light ↔ dark; clearing storage falls
back to the OS `prefers-color-scheme`. Theme changes dispatch a `themechange`
event for components that need to re-render.

### Accessibility

- Semantic landmarks on every page (`<nav>`, `<main>`, `<footer>`).
- Visible focus rings on all interactive elements (`--shadow-focus`).
- All maps and decorative SVGs have `role="img"` / `aria-label` / `aria-hidden`.
- Forms use proper `<label>` elements and required ARIA states.
- Animations respect `prefers-reduced-motion`.
- All buttons are reachable via keyboard; the carousel responds to ←/→.

### Maps

`frontend/static/js/leaflet-map.js` lazy-loads Leaflet 1.9.4 from unpkg the
first time a map is needed and configures **OpenStreetMap** tiles only — no
Mapbox, no Google. Custom popup and marker styles match the design system.

### Connecting the API

Every page module calls `window.api` against `/api/*`. Endpoints that aren't
implemented yet show empty states with skeletons, so the UI never breaks.
