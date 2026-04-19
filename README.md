# Openclaw Command Center

A polished internal dashboard for running Daniel's businesses. Ships with
JobCarver stats, a calendar, an assistant control panel, a storage vault and
a pluggable layer for adding more brands (CohesionSupps next) without a
redesign.

- **Frontend:** SvelteKit + TailwindCSS
- **Backend:** FastAPI
- **Database:** SQLite (stdlib `sqlite3`, WAL mode)
- **Auth:** single-user, signed-cookie session
- **Storage:** local filesystem behind a swappable `StorageBackend` protocol

## Quick start

```bash
cp .env.example .env
# edit .env: set ADMIN_PASSWORD and SESSION_SECRET at minimum
```

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

The first launch creates `backend/data/app.db` and `backend/data/uploads/`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and log in with `ADMIN_PASSWORD`. After signing in
you'll pick a profile (Daniel or Partner) so the assistant knows who's at
the keyboard. You can rename profiles from `/profiles` and switch any time
from the topbar.

> **Note on profiles vs. auth.** Profiles are *identity*, not authorization.
> The app is single-password; profiles let Mia tailor her replies and tag
> activity by user. Anyone with the password can switch profiles.

## Project layout

```
backend/   FastAPI app, SQLite schema, business providers, vault storage
frontend/  SvelteKit app, Tailwind theme, reusable components, pages
```

See [the plan](.cursor/plans) for full architectural notes.

## Adding a new business

1. Implement `BusinessStatsProvider` in
   `backend/app/businesses/<slug>.py`.
2. Register it in `backend/app/businesses/__init__.py`.
3. The dashboard and `/businesses/<slug>` page light up automatically.

## Adding a new assistant skill

Edit `backend/app/data/skills.json` and add an entry. The skills page
re-renders on next load.

## Tests

```bash
cd backend && pytest
cd frontend && npm run check && npm test
```

## Security notes

- Secrets are read from `.env` (never commit it). `.env.example` documents
  every variable.
- Login is rate-limited in-memory.
- Uploads are size + mime validated, content-hashed for de-dup, and served
  with `X-Content-Type-Options: nosniff`.
- Cookies are HTTP-only, SameSite=Lax, and `Secure` when `FRONTEND_ORIGIN`
  is HTTPS.

## Deploying

The backend is a single ASGI app (`app.main:app`) — run behind any process
manager (uvicorn, gunicorn, systemd, Railway, Fly). The frontend builds
with `@sveltejs/adapter-node` and can run on the same host or be served
statically. Point `PUBLIC_API_BASE` at the public backend URL.

## Follow-ups / next steps

- Wire `JOBCARVER_STATS_URL` to the real upstream endpoint.
- Add the CohesionSupps provider implementation when its stats API exists.
- Swap `LocalStorage` for an S3 implementation by adding
  `backend/app/storage/s3.py` and selecting it via env.
