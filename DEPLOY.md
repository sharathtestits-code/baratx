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

## 1b. Email (done)

- Cloudflare Email Routing: **Enabled**, DNS **Locked**
- Destination: `sharathtestits@gmail.com` (verified)
- Rule: **`hello@barathx.com` → Gmail** (Active)
- Catch-all: Drop / Disabled (only `hello@` receives mail)

## 1c. Next accounts

1. Create Railway account for API hosting
2. MSG91 later for SMS OTP


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

Wire production into the app code:

- Read `DATABASE_URL` / `CORS_ORIGINS` / `ENVIRONMENT` from env
- Real MSG91 OTP (hide `dev_otp` when `ENVIRONMENT=production`)
- R2/S3 media uploads instead of local `/media`
- Landing copy: English-only + “more languages coming”

Say when accounts + domain are bought and we will do that wiring.
