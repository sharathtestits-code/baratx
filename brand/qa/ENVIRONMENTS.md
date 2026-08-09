# BarathX — Environments (QA vs Production)

Keep these separate. Automation agents and Playwright must use **QA**, never Production, unless ops explicitly request a prod smoke.

**Status (2026-08-09):** Production is live. **QA API+SPA is live** on Railway interim URL below. Custom host `qa.barathx.com` still needs Cloudflare DNS (currently redirects to a link page).

| | **QA (staging)** | **Production (prod)** |
|---|---|---|
| **Web app** | Interim: `https://baratx-production-f8ce.up.railway.app` · Custom (pending DNS): `https://qa.barathx.com` | `https://barathx.com` |
| **API** | Same origin as QA web (Railway `baratx-qa` project) | `https://baratx-production.up.railway.app` |
| **API docs** | `https://baratx-production-f8ce.up.railway.app/docs` | `https://baratx-production.up.railway.app/docs` |
| **Admin** | Interim `/admin` on the Railway URL · later `https://qa.barathx.com/admin` | `https://barathx.com/admin` |
| **DB** | Separate Railway Postgres (`baratx-qa`) | Production Postgres |
| **Secrets** | QA-only vars on Railway service `baratx` | Prod secrets — never in QA docs |

### Cloudflare Pages (frontend)

| Env | Project / branch | `VITE_API_BASE` |
|-----|------------------|-----------------|
| QA | Pages project `baratx-qa` · branch `main` or `qa` | `https://baratx-qa.up.railway.app` |
| Prod | Pages project `baratx` · production | `https://baratx-production.up.railway.app` |

Optional interim QA frontend if DNS not ready: `https://baratx-qa.pages.dev`.

### Agent / E2E env (copy `env.qa.example` → repo-root `.env.qa` — gitignored)

```bash
# QA only — do not point these at production
QA_BASE_URL=https://qa.barathx.com
QA_API_BASE=https://baratx-qa.up.railway.app

# Prod (reference only — not for automation)
PROD_BASE_URL=https://barathx.com
PROD_API_BASE=https://baratx-production.up.railway.app

QA_USER_A_EMAIL=
QA_USER_A_PASSWORD=
QA_USER_B_EMAIL=
QA_USER_B_PASSWORD=
QA_OFFICIAL_USER=sharath
QA_OFFICIAL_PASSWORD=
QA_ADMIN_SECRET=
```

### Rules

1. Feature matrix + Playwright default to **QA_*** URLs.  
2. Never run destructive admin actions (delete user, force IG) on **prod**.  
3. When QA service is not provisioned yet, follow `brand/qa/PROVISION.md` (script `scripts/provision-qa.sh` or Railway dashboard + Cloudflare DNS) before enabling CI.  
4. Prod remains the live user-facing stack in `DEPLOY.md`.
