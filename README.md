# MiPeli-Backend

API for [MiPeli](https://github.com/Andreysillo/MiPeli-Frontend): FastAPI on Render, MongoDB Atlas, with TMDB, OMDb and (optionally) TasteDive behind a cache with soft expiry. The contract with the frontend is in the frontend repo, `docs/recomendacion.md`.

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; on Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # fill in MONGODB_URI (never commit .env)
uvicorn app.main:app --reload
```

`GET /health` answers without touching the database.

## Quality

```bash
ruff check .
pytest
```

## Layout

```
app/main.py     FastAPI, CORS (Vercel + localhost), lifespan that opens/closes Mongo and creates the TTL index
app/config.py   settings from environment variables
app/cache.py    get_or_fetch: soft expiry + stale-if-error; one "cache" collection, TTL index only cleans abandoned data
tests/          health and cache (fresh, expired, API down)
render.yaml     Render Blueprint (free plan, health check, deploys after CI passes)
```
