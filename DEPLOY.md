# BaratX — Domain & hosting setup (Step 3)

English-only public path. Do these in order. You must complete payments/signups in the browser — this file is the checklist.

## 0. Project location (done)

- Local path: `~/Projects/barathx` (not Google Drive)
- Git initialized on `main`
- Backend venv + frontend `node_modules` reinstalled
- Local secrets file: `backend/.env` (gitignored)

## 1. Domain (done)

- Registrar: **Porkbun**
- Domain: **`barathx.com`**
- Cloudflare: **Active** — nameservers set to:
  - `adelaide.ns.cloudflare.com`
  - `aragorn.ns.cloudflare.com`
- DNS verified live (dig NS returns Cloudflare)

## 1b. Email (inbound vs outbound)

**Inbound (done):** Cloudflare Email Routing
- Destination: `sharathtestits@gmail.com`
- Rule: `hello@barathx.com` → Gmail

**Outbound activation email (app code ready):**
Cloudflare Routing cannot *send*. Prefer **Resend** from `hello@barathx.com` (verify `barathx.com` in Resend). Keep Gmail SMTP as backup/debug only.

```
FRONTEND_URL=https://barathx.com
EMAIL_FROM=BaratX <hello@barathx.com>
RESEND_API_KEY=re_xxx
# Optional backup/debug (ignored when RESEND_API_KEY is set):
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=sharathtestits@gmail.com
# SMTP_PASSWORD=<gmail-app-password>
```

Without Resend/SMTP, local/dev still creates accounts and shows a **dev verify link** in the banner.

## 1c. Hosting accounts

1. **Railway** (done — API + Postgres + env vars)
   - Project: `charming-sparkle` / service `baratx`
   - Public URL: https://baratx-production.up.railway.app
   - Docs: https://baratx-production.up.railway.app/docs
   - Vars set: `DATABASE_URL`, `JWT_SECRET`, `ENVIRONMENT`, `CORS_ORIGINS`
   - Optional: `ADMIN_SECRET` for the registrations page at https://barathx.com/admin
2. MSG91 later for SMS OTP

### See who registered / post as BaratX

1. Set `ADMIN_SECRET` on the Railway API service (long random string).
2. Redeploy the API if needed.
3. Open https://barathx.com/admin and enter that secret.
4. You’ll see total users, last 24h / 7d counts, a newest-first list, and **Post as BaratX**.

### Log in as official @baratx (optional)

1. Set `OFFICIAL_ACCOUNT_PASSWORD` on the Railway API (strong password).
2. Redeploy / restart so seed can sync the hash.
3. On https://barathx.com/login use username `baratx` (or email `baratx@barathx.com`) + that password.
4. Same password works for `@bharatvoices` and `@indiatech`.

### Railway deploy notes

- Repo: `sharathtestits-code/baratx`
- Root `Dockerfile` + `railway.toml` build the **backend** from the monorepo (do not set Root Directory, or leave it `/`)
- Alternate: Root Directory = `backend` uses `backend/Dockerfile`
- After Postgres is added, set on the API service:
  - `DATABASE_URL=${{Postgres.DATABASE_URL}}` (or Railway’s variable reference UI)
  - `JWT_SECRET` = long random string
  - `ENVIRONMENT=production`
  - `CORS_ORIGINS` = frontend URL when ready
  - `ADMIN_SECRET` = long random string (for /admin)


## 2. Create free accounts (no code yet)

Open and sign up with the same email:

1. **Cloudflare** — https://dash.cloudflare.com/sign-up  
   - Add your domain  
   - Later: Pages (frontend) + R2 (images)

2. **Railway** (recommended API host) — https://railway.app  
   - Or **Render**: https://render.com  
   - You will deploy `backend/` with the included `Dockerfile`

3. **MSG91** (India SMS OTP) — https://msg91.com  
   - Needed before real phone signups  
   - Until then, local/dev OTP still works

4. **GitHub** (optional but useful) — push this repo, connect Railway + Pages for auto-deploy

## 3. After accounts exist — deploy order

1. Create **Postgres** plugin on Railway/Render → copy `DATABASE_URL`
2. Create **R2 bucket** `baratx-media` on Cloudflare → API tokens
3. Deploy backend with env vars from `backend/.env.example` (production values)
4. Build frontend with `VITE_API_BASE=https://api.<your-domain>`
5. Deploy frontend to Cloudflare Pages
6. Attach custom domains + HTTPS
7. Test: signup → OTP → post with image → profile

## 4. Rough first-month cost

| Item | Ballpark |
|------|----------|
| Domain | ₹700–1,500 / year |
| Cloudflare Pages + R2 | Free tier usually enough |
| Railway/Render + Postgres | ~₹500–1,500 / month |
| MSG91 OTP tests | ~₹200–500 to start |
| **Total to go live** | **~₹2–4K first month** |

## 5. What is NOT done yet (next coding step)

Done already: `CORS_ORIGINS`, hide `dev_otp` in production, email verify via Resend, Google sign-in.

Still open:

- Real MSG91 OTP SMS (phone auth still demo until SMS is wired)
- R2/S3 media uploads instead of local `/media`
- Landing copy: English-only + “more languages coming”

Say when you want MSG91 or R2 and we will wire those next.
