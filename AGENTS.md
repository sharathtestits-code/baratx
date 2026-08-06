# AGENTS.md

## Cursor Cloud specific instructions

BaratX is a two-service app: a FastAPI backend (`backend/`) and a React + Vite
frontend (`frontend/`). Standard run/setup commands live in `README.md`,
`backend/README.md`, and `frontend/README.md`; the notes below only cover
non-obvious caveats for running things here.

### Services

- Backend: FastAPI served by uvicorn on port `8000`. Run from `backend/` with
  the venv created during setup: `./venv/bin/uvicorn app.main:app --reload --port 8000 --env-file .env`.
  Interactive API docs at `http://localhost:8000/docs`; health check at `/health`.
- Frontend: Vite dev server on port `5173` (`npm run dev` from `frontend/`). It
  talks to the backend via `VITE_API_BASE` (defaults to `http://localhost:8000`
  from `.env.example`), so start the backend first.

### Non-obvious caveats

- The backend does NOT auto-load `backend/.env` (no `python-dotenv` call in the
  app). Its defaults already work for dev (SQLite `indiavoice.db`, a dev
  `JWT_SECRET`, CORS for `localhost:5173`). To apply a custom `.env`, pass it to
  uvicorn with `--env-file .env` rather than expecting it to be picked up
  automatically.
- The SQLite DB (`backend/indiavoice.db`) is created automatically on first
  boot, and lightweight column migrations run on startup in
  `app.main.run_migrations()`. There is no separate migration command.
- `POST /posts` expects `multipart/form-data` (field `text`, optional `image`),
  not JSON. Most other endpoints are JSON.
- Phone OTP is not sent via SMS in dev: the signup/login response includes the
  code as `dev_otp`. Email signup likewise returns a `dev_verify_url` instead of
  sending a real email.
- On startup the app seeds official accounts (`@baratx`, `@bharatvoices`,
  `@indiatech`) and starter communities; these appear in the feed by default.
- There are currently no automated tests and no lint tooling configured in this
  repo, so there is nothing to run for lint/test.
