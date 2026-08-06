# BaratX

India-first public square (English now; more languages later). Backend is
FastAPI + SQLite (local), frontend is React (Vite).

**Brand:** BaratX · **Domain:** barathx.com (kept as purchased)

**Canonical local path:** `~/Projects/barathx` (do not run from Google Drive).

Public hosting checklist: see [DEPLOY.md](./DEPLOY.md).
Android / App Store (Capacitor): see [MOBILE.md](./MOBILE.md).

## Structure

```
barathx/
  backend/     FastAPI — auth, feed, posts, social graph
  frontend/    React (Vite) — landing, feed, profiles
  frontend/android/   Capacitor Android project (com.baratx.app)
  frontend/ios/       Capacitor iOS project (com.baratx.app)
```

## Run it

### 1. Backend

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs

### 2. Frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

Open the URL it prints (usually http://localhost:5173).

### 3. Native apps (Capacitor)

```
cd frontend
npm run build:app
npm run open:android   # Android Studio
npm run open:ios       # Xcode (macOS)
```

Full Play Store / App Store packaging steps: [MOBILE.md](./MOBILE.md).

## What's implemented

- Email + password signup/login
- Phone + OTP signup/login (India-style flow — most Indian users sign up
  with phone, not email)
- JWT session tokens
- Profile page (`/users/me`) and public profile lookup (`/users/{username}`)
- Basic dashboard placeholder page after login

## What's stubbed / needs work before real users

- **Phone OTP is not sent via real SMS.** The backend returns the code
  directly in the API response (`dev_otp`) so you can test the flow without
  paying for an SMS provider. Before any real signups, wire in MSG91, Twilio
  Verify, or similar, and remove `dev_otp` from the response.
- **Email verification is not enforced.** `is_email_verified` is stored but
  nothing sends a verification email yet.
- **No rate limiting on OTP requests** — needed before production to stop
  SMS-bombing abuse.
- Language selection (Telugu/Hindi/English) was intentionally left out of
  this pass — `language` defaults to `"en"` on every account and is ready
  to be added to the signup form and used to drive UI translation later.
- No password reset flow yet.

## Compliance note (India)

Once this crosses 5M users it becomes a "Significant Social Media
Intermediary" under India's IT Rules, requiring a Resident Grievance
Officer, Chief Compliance Officer, and Nodal Contact Person, plus a
grievance/appeals workflow with fixed response timelines (24hr
acknowledgment, 7-day resolution). Worth designing the moderation/reporting
data model with this in mind before it's bolted on under time pressure.

## Important: don't run this from inside a cloud-sync folder

If this project lives inside Google Drive, Dropbox, or OneDrive's sync
folder, Python virtual environments and `node_modules` can fail to sync
properly or go missing (this happened once already). If you hit strange
"file not found" errors, move the whole `indiavoice` folder to a local,
non-synced location (e.g. `~/Desktop` or `~/Projects`) and run it from
there instead.
