# BharatX — Domain & hosting setup (Step 3)

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
EMAIL_FROM=BharatX <hello@barathx.com>
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

### See who registered / post & comment as BharatX

1. Set `ADMIN_SECRET` on the Railway API service (long random string).
2. Redeploy the API if needed.
3. Open https://barathx.com/admin and enter that secret.
4. You’ll see total users, last 24h / 7d counts, a newest-first list, **Post as BharatX**, and **Comment on new users** (reply to recent posts from new joiners).

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

## 5. Why uploaded images disappeared

Railway wipes the **container disk** on every deploy/restart. Images were saved
under local `/media`, so files vanished while post rows stayed in Postgres
(URLs like `/media/….png` then 404).

**Fix:** new uploads are stored in Postgres (`media_assets`) on Railway and
served from `/media/{id}`. Old broken `/media/…` files from before this fix
cannot be recovered — re-upload those.

At scale, switch to Cloudflare R2:

```
MEDIA_BACKEND=s3
S3_BUCKET=baratx-media
S3_ENDPOINT_URL=https://<accountid>.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=…
S3_SECRET_ACCESS_KEY=…
S3_PUBLIC_BASE_URL=https://media.yourdomain.com
```

## 6. Video & audio (Instagram-like) — what it takes

Not built yet. To add IG-style video/audio you’d need:

1. **Object storage (required)** — R2/S3/Cloudinary. Video in Postgres is not viable.
2. **Upload API** — accept `video/mp4`, `video/webm`, `audio/mpeg`, `audio/mp4`; caps ~50–100MB video, ~15MB audio.
3. **Transcoding** — ffmpeg (or Cloudflare Stream / Mux) for mobile-friendly H.264 + poster thumbnails.
4. **Feed UI** — `<video>` / `<audio>` players, mute-by-default, autoplay in viewport, progress scrubber.
5. **CDN + range requests** — streaming, not full-file download.
6. **Moderation** — size/duration limits, optional NSFW checks later.

Rough build: storage wiring + upload endpoints + players first; transcoding/CDN next.

## 7. What is NOT done yet (next coding step)

Done already: durable image storage (DB blobs), arenas incl. Startups/Spirituality, topic taxonomy.

Still open:

- Real MSG91 OTP SMS (phone auth still demo until SMS is wired)
- R2/S3 for images at scale + video/audio pipeline
- Landing copy: English-only + “more languages coming”

Say when you want MSG91 or video/audio and we will wire that next.
