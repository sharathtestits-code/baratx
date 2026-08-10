# BarathX — Environments (QA vs Production)

Keep these separate. Automation agents and Playwright must use **QA**, never Production, unless ops explicitly request a prod smoke.

**Git:** `main` = PROD · `qa` = QA · `dev` = development — see [BRANCHING.md](./BRANCHING.md).

| | **QA (staging)** | **Production (prod)** |
|---|---|---|
| **Git branch** | **`qa`** | **`main`** |
| **Web app** | `https://qa.barathx.com` | `https://barathx.com` |
| **API** | `https://baratx-qa.up.railway.app` | `https://baratx-production.up.railway.app` |
| **API docs** | `https://baratx-qa.up.railway.app/docs` | `https://baratx-production.up.railway.app/docs` |
| **Ops console** | Owner-only (`@sharath` + unlock) at `/bx-ops` — others get 404 | Same |
| **DB** | Separate Railway Postgres (QA) | Production Postgres |
| **Secrets** | `ADMIN_SECRET` / passwords for QA only | Prod secrets — never in QA docs |

### Cloudflare Pages (frontend)

| Env | Project / branch | `VITE_API_BASE` | `VITE_PUBLIC_URL` (OG tags) |
|-----|------------------|-----------------|------------------------------|
| QA | Pages project `baratx-qa` · branch **`qa`** | `https://baratx-qa.up.railway.app` (or empty if same-origin proxy) | `https://qa.barathx.com` |
| Prod | Pages project `baratx` · branch **`main`** | `https://baratx-production.up.railway.app` | `https://barathx.com` |

### Railway API

| Env | Service deploy branch | Notes |
|-----|----------------------|--------|
| QA | **`qa`** | `ENVIRONMENT=qa` |
| Prod | **`main`** | `ENVIRONMENT=production` |

### Railway API env (critical for email links)

| Var | QA | Production |
|-----|----|------------|
| `ENVIRONMENT` | `qa` | `production` |
| `FRONTEND_URL` | `https://qa.barathx.com` | `https://barathx.com` |
| `CORS_ORIGINS` | include `https://qa.barathx.com` | include `https://barathx.com` |

Never set `FRONTEND_URL` to a `*.up.railway.app` host — verify/reset emails must use the public web domain. The API hardens common misconfigs, but ops should still set the vars correctly.

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
3. Promote code: `dev` → `qa` → `main` (prod). Wire Cloudflare Pages QA + Railway QA to watch **`qa`**, not `main`.  
4. Prod remains the live user-facing stack in `DEPLOY.md`.  
5. `dev` is for integration; it should not deploy to barathx.com or qa.barathx.com.
