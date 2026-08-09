## Live now (2026-08-09)

| | URL |
|---|---|
| **QA app + API (use this)** | https://baratx-production-f8ce.up.railway.app |
| Health | https://baratx-production-f8ce.up.railway.app/health → `{"status":"ok"}` |
| Admin | https://baratx-production-f8ce.up.railway.app/admin |
| Railway project | `baratx-qa` |

`ADMIN_SECRET` / official password: Railway → project **baratx-qa** → service **baratx** → **Variables**.

### Finish `qa.barathx.com` (Cloudflare DNS)

Railway expects:

| Type | Name | Value |
|---|---|---|
| CNAME | `qa` | `qsj314oe.up.railway.app` |
| TXT | `_railway-verify.qa` | `railway-verify=6bc01a7c8d4605bbc3c1b58fc3623abcb32704da32ab6399fcf7a732a1e6adbc` |

Also **delete** any Redirect Rule / Bulk Redirect that sends `qa.barathx.com` → `l.ink`.

Until DNS is fixed, use the Railway interim URL above for QA testing.

---

# Provision BarathX QA (bring `qa.barathx.com` up)

QA is **not** a second copy of the git repo — it is a separate Railway service + DB, then DNS.

| | Target |
|---|---|
| App + API (same origin) | `https://qa.barathx.com` → Railway `baratx-qa` |
| Interim (before DNS) | `https://baratx-qa.up.railway.app` (or the domain Railway generates) |
| DB | Separate Postgres (never production) |
| Secrets | Separate `ADMIN_SECRET` / `JWT_SECRET` |

Prod stays at `https://barathx.com` + `https://baratx-production.up.railway.app`.

---

## Fast path (agent / CLI)

1. Create a **Railway account token**: https://railway.com/account/tokens  
2. Optional — Cloudflare API token with **Zone → DNS → Edit** on `barathx.com`.  
3. In this repo:

```bash
export RAILWAY_API_TOKEN='…'
# optional:
export CLOUDFLARE_API_TOKEN='…'
./scripts/provision-qa.sh
```

4. Wait for deploy (Railway dashboard → `baratx-qa` → Deployments).  
5. Verify:

```bash
curl -sS https://baratx-qa.up.railway.app/health
# expect {"status":"ok"}
```

6. Secrets written locally to `~/.config/baratx/qa.secrets.env` (gitignored path). Put `QA_ADMIN_SECRET` into your local `.env.qa` for testers.

Or paste `RAILWAY_API_TOKEN` (and optional `CLOUDFLARE_API_TOKEN`) into the Cursor cloud agent chat and ask it to run `./scripts/provision-qa.sh`.

---

## Click path (Railway dashboard)

Use this if you prefer the UI.

### A. Railway project

1. Open https://railway.com/project/83b2f710-3b06-4d37-8e7b-94e3821e42fc (prod `charming-sparkle`) **or** create a **new** project named `baratx-qa` (preferred — isolates QA spend/logs).  
2. **New project `baratx-qa`:**
   - **Add** → **Database** → **PostgreSQL**
   - **Add** → **GitHub Repo** → `sharathtestits-code/baratx` → branch `main`  
   - Service name: `baratx`  
   - Root directory: `/` (uses root `Dockerfile` — API + SPA same origin)  
3. **Variables** on service `baratx` (Variables tab):

| Key | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (pick via Variable Reference) |
| `ENVIRONMENT` | `qa` |
| `JWT_SECRET` | long random |
| `ADMIN_SECRET` | long random (QA only) |
| `OFFICIAL_ACCOUNT_PASSWORD` | strong password for `@baratx` on QA |
| `FRONTEND_URL` | `https://qa.barathx.com` |
| `CORS_ORIGINS` | `https://qa.barathx.com,https://baratx-qa.up.railway.app` |
| `EMAIL_FROM` | `BarathX QA <hello@barathx.com>` |
| `MEDIA_BACKEND` | `auto` |
| `GOOGLE_CLIENT_ID` | same as prod (optional) |

4. **Settings → Networking → Generate Domain**  
   - Prefer setting the public hostname to something like `baratx-qa.up.railway.app` if Railway allows a custom subdomain label; otherwise copy whatever `*.up.railway.app` it gives you and update docs/`CORS_ORIGINS`.  
5. **Custom domain:** add `qa.barathx.com` → copy the CNAME target Railway shows.

### B. Cloudflare DNS (`barathx.com`)

Today `qa.barathx.com` **302s to a link-in-bio** (`barathx-com.l.ink`). That must be removed.

1. https://dash.cloudflare.com → domain **barathx.com**  
2. **DNS** → delete any A/CNAME/AAAA for `qa` that is not Railway.  
3. Add: **CNAME** `qa` → `<railway-service-domain>` → Proxied.  
4. **Rules → Redirect Rules / Bulk Redirects** — delete anything matching `qa.barathx.com` → `l.ink`.  
5. Wait 1–2 minutes → open https://qa.barathx.com

### C. Optional Cloudflare Pages

Not required if Railway serves the SPA (root Dockerfile does).  
Only add Pages project `baratx-qa` if you want CDN-split frontend; then set `VITE_API_BASE` to the QA Railway API URL and use workflow `.github/workflows/deploy-qa-pages.yml`.

---

## Smoke checklist

- [ ] `GET https://<qa-railway>/health` → `{"status":"ok"}`  
- [ ] `GET https://qa.barathx.com/` loads Square shell (not l.ink)  
- [ ] `/admin` unlocks with **QA** `ADMIN_SECRET` (not prod)  
- [ ] Create a test user on QA — confirm it does **not** appear in prod admin  
- [ ] Copy URLs into `brand/qa/env.qa.example` → local `.env.qa`

---

## Do not

- Point QA `DATABASE_URL` at production Postgres  
- Reuse production `ADMIN_SECRET` / `JWT_SECRET`  
- Run destructive Playwright admin tests against `barathx.com`
