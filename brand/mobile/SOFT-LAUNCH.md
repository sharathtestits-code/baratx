# BaratX mobile soft launch (Gen Z)
Updated: **2026-08-09**

**Why:** Indian Gen Z prefers apps over browser. Soft-launch Android first, iOS second.

Capacitor shells already exist (`com.baratx.app`). This is the ship checklist.

---

## Priority order

| # | Track | Why |
|---|---|---|
| 1 | **Android — Play Internal / Closed testing** | Fastest path; most Indian Gen Z |
| 2 | Direct APK to Campus Voices (optional) | Same-day while Play review waits |
| 3 | **iOS TestFlight** | Needs Mac + Apple Developer ($99/yr) |

Do **not** wait for public Production store listing to start Campus Voice testing.

---

## Blockers before inviting Gen Z

| Blocker | Status | Action |
|---|---|---|
| Privacy Policy URL | **Added** `/privacy` | Deploy frontend so https://barathx.com/privacy works |
| Terms of Service URL | **Added** `/terms` | Deploy frontend so https://barathx.com/terms works |
| Real SMS OTP (MSG91) | Often demo OTP in API | Soft launch **needs real OTP** — set `MSG91_AUTH_KEY` + `MSG91_TEMPLATE_ID` on Railway |
| Google Sign-In in app | **Wired** — needs Cloud SHA-1 | Create Android OAuth client (`com.baratx.app` + SHA-1). Phone OTP still works. |
| Play Console account | You | Create / pay $25 one-time |
| Apple Developer | You | $99/year — only when iOS week starts |
| Release keystore | You | Generate once; never commit |

---

## A. Today / this week — Android soft launch

### 1) Accounts & legal (30–60 min)
- [ ] Confirm https://barathx.com/privacy and `/terms` load after deploy
- [ ] Create [Google Play Console](https://play.google.com/console) app: **BaratX** / package `com.baratx.app`
- [ ] Store listing draft (below)
- [ ] Privacy policy URL in Play Console: `https://barathx.com/privacy`

### 2) Wire real phone OTP (critical for India Gen Z)
On Railway API service set:
```
MSG91_AUTH_KEY=...
MSG91_TEMPLATE_ID=...
MSG91_SENDER_ID=BARATX
```
Redeploy. Test OTP on a real Indian number from web first, then app.

### 3) Build release AAB (on a machine with Android Studio)

```bash
cd frontend
npm install
npm run build:app
npm run open:android
```

One-time keystore:
```bash
keytool -genkey -v -keystore ~/baratx-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias baratx
```

In Android Studio: **Build → Generate Signed Bundle → Android App Bundle**  
Current version: **0.1.0** (versionCode **2**).

### 4) Play — Internal testing (same day possible)
1. Play Console → Testing → **Internal testing**
2. Upload AAB
3. Add testers (email list): you + 10–20 Campus Voices / friends
4. Share the Internal testing link in WhatsApp channel:
   https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o

### 5) Optional same-day APK
```bash
cd frontend/android
./gradlew assembleDebug
# app/build/outputs/apk/debug/app-debug.apk
```
Send APK only to trusted testers (not public). Prefer Play Internal for updates.

---

## B. iOS soft launch (after Android is in testers’ hands)

Full App Store / TestFlight checklist: **[APP-STORE-IOS.md](./APP-STORE-IOS.md)**

On a **Mac**:
```bash
cd frontend
npm run build:app
npm run open:ios
```
1. Xcode → Signing → your Team · Bundle ID `com.baratx.app`
2. Version **0.1.0**, bump build number each upload
3. Archive → Distribute → App Store Connect
4. Enable **TestFlight** → invite Campus Voices by email
5. Privacy URL: `https://barathx.com/privacy`

---

## C. Soft-launch store listing copy (Independence Day · 15 August)

**Title:** BarathX  
**Short description (≤80 chars):**  
Official soft launch · India’s public square — pick a side, argue it live.

**Full description:**
```
BarathX is India’s public square.

Official soft launch on Independence Day — 15 August — in the browser (phone & desktop). iOS and Android apps coming soon.

Short posts. Real sides. Real debate.

• Square — drop a take, get real replies
• Arenas — Sports, Politics, Entertainment, News, Startups, Spirituality
• Live rooms — pick a side, argue now (optional Live Talk audio)
• Human takes only. No AI slop.

No endless Reels feed inside the app.
Just say it. Prove it.

Join early → leave your first take → https://barathx.com
```

**Category:** Social  
**Tags:** debate, India, social, campus, startups, Independence Day  
**Contact:** hello@barathx.com  
**WhatsApp:** https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o

### Screenshots needed (phone)
1. Landing / signup (phone OTP)  
2. Feed with a real take  
3. Arena (Entertainment) with sides  
4. Reply thread  
5. Profile  

Capture from emulator or device after `build:app`.

---

## D. Soft-launch tester script (send to Campus Voices)

```
BarathX soft launch (Independence Day) — install + first take

1) Open https://barathx.com OR Play Internal / TestFlight link
2) Sign up (Google or phone OTP)
3) Complete first take + quick nav tour (Square · Live · Arenas · Alerts · You)
4) Open Entertainment → leave 1 take with a side
5) Reply to someone else’s take
6) Try Settings → Appearance (theme)
7) Join WhatsApp: https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o

Bug? Screenshot + send to me.
```

---

## E. Success for soft launch week

- [ ] ≥20 Android installs (Internal testing)
- [ ] ≥15 accounts created via **phone OTP**
- [ ] ≥10 users with **first post + side** (activation)
- [ ] ≥3 Entertainment debates with ≥5 real replies
- [ ] Crash-free open → feed → post path
- [ ] iOS TestFlight started (if Mac available)

---

## What’s already in the repo

- Capacitor Android + iOS projects
- App id `com.baratx.app`, splash/status bar branded
- Phone/email auth against production API
- Native back button + keyboard handling (`src/native.js`)
- Privacy + Terms pages for store URLs

## What you still do outside git

Play/App Store accounts · signing keys · MSG91 live SMS · screenshots upload · tester invites
