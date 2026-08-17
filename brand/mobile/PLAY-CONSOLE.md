# BarathX — Play Console: get the Android app going

**Package:** `com.baratx.app`  
**Status as of 17 Aug 2026:** Draft app. **Internal testing = Active**. Closed testing and Production are locked until you finish app setup.

Internal testing **does not** wait on store listing. Closed testing **does**. Production on a new personal Play account **does**, plus 12 testers for 14 days.

---

## What is already done

| Item | Status |
|------|--------|
| Play app created | Yes — BarathX / `com.baratx.app` |
| Internal testing release | **Active** (Not reviewed is normal for internal) |
| Privacy policy live | https://barathx.com/privacy |
| Terms live | https://barathx.com/terms |
| AAB / version in repo | `0.1.2` (versionCode 4) |

You do **not** need another internal release to start testers.

---

## Do this today (testers can install now)

Internal testing is the fastest way Campus Voices get the app. Closed testing can wait until listing tasks are filled.

1. Play Console → **BarathX** → **Test and release → Testing → Internal testing**.
2. Open the **Testers** tab.
3. Add emails (you + 10–20 Campus Voices). Save.
4. Copy the **opt-in link** (looks like `https://play.google.com/apps/internaltest/...`).
5. Send the message in [§ Tester invite](#tester-invite).

Each tester must, **on an Android phone signed into that Gmail**:

1. Open the opt-in link.
2. Tap **Become a tester** / Accept.
3. Tap **Download it on Google Play** and install from Play Store.

If they search “BarathX” on Play without opting in first, the app will look missing. That is expected for a draft.

Keep this track running. It does **not** count toward Google’s 12-tester / 14-day production rule. Closed testing does.

---

## Unlock closed testing (the real blocker)

Dashboard says **Finish setting up your app → Provide app information and create your store listing**. Until those tasks are green, **Closed testing stays locked**.

Click **View tasks** on the dashboard. Work the list top to bottom. Typical items:

### 1) Main store listing

**Grow users → Store presence → Main store listing**

Paste the copy below. Upload assets from `brand/mobile/play-listing/`.

| Field | Value |
|-------|--------|
| App name | BarathX |
| Short description | India's public square — pick a side, argue it live. |
| Full description | See [§ Store listing copy](#store-listing-copy) |
| App icon | `play-listing/icon-512.png` (512×512) |
| Feature graphic | `play-listing/feature-1024x500.png` (1024×500) |
| Phone screenshots | At least **2** (need 2–8). Capture on a real phone — see [§ Screenshots](#screenshots) |
| Privacy policy | `https://barathx.com/privacy` |

**Category:** Social  
**Tags:** debate, social, india, campus, news, sports  
**Email:** hello@barathx.com  
**Website:** https://barathx.com  
**WhatsApp (optional contact):** https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o

### 2) Store settings

**Grow users → Store presence → Store settings**

- App name: BarathX
- Default language: English (United States) or English (India) — pick one and stay consistent
- Contact email: hello@barathx.com
- Phone / website: optional; website https://barathx.com

### 3) Target audience and content

**Policy → Target audience and content**

- Target age: **18 and over only**. Do **not** tick 13–15 or 16–17. The product is 18+.
- Appeal to children: **No**
- News app: **No** (primary use is debate/social, not a news publisher)
- COVID contact tracing: **No**

### 4) Content ratings

**Policy → App content → Content ratings** → IARC questionnaire.

Answer honestly for a social / UGC debate app:

- Category: **Social Networking** (or Communication, if that is the closest option)
- Users can communicate: **Yes** (posts, replies, live rooms)
- User-generated content: **Yes**
- Users can share location: **No** (unless you later add it)
- Shares user's physical location: **No**
- In-app purchases: **No**
- Ads: **No**
- Violence / sexual content as a core feature: **No**
- Mild language possible in UGC: **Yes** if asked
- Age gate in app: **Yes — 18+**

Submit and wait for the rating email. Assign the rating to the app when it arrives.

### 5) News apps

**No** — BarathX is not a news publication.

### 6) Data safety

**Policy → App content → Data safety**

| Question | Answer |
|----------|--------|
| Collects user data? | **Yes** |
| Encrypted in transit? | **Yes** (HTTPS) |
| Users can request deletion? | **Yes** — hello@barathx.com |
| Independent security review? | **No** |
| Sold / shared for ads? | **No** |

Data types to declare (collected for **App functionality** + **Account management**, not sold):

- **Personal info:** Name, Email, Phone number (account)
- **User content:** Posts, replies, photos the user uploads
- **App activity / identifiers:** App interactions, crash logs if Play collects them, device/session needed to stay signed in

Optional vs required: account fields are **required** to create an account. Photos are **optional**.

### 7) Ads

**Does your app contain ads?** → **No**

### 8) App access (reviewer login)

**Policy → App content → App access**

- All or some functionality is **restricted** (login required).
- Add **instructions + a test account** Play reviewers can use:
  - Email/password **or** a phone number that receives OTP
  - Steps: open app → Sign in → land on Square → open an Arena → post a take
- Do **not** leave this blank. Reviewers reject social apps they cannot log into.

### 9) Government / Financial / Health

All **No** (Founding 100 thank-you is not an in-app purchase or financial product).

### 10) Countries / countries available for testing

When you create the **closed** release, include **India** plus every country a tester’s Google account is in. If a tester is abroad and India-only is selected, install fails.

---

## Store listing copy

**Short description** (80 characters max — this is 52):

```
India's public square — pick a side, argue it live.
```

**Full description:**

```
BarathX is India's public square.

Short posts. Real sides. Real debate.

• Square — drop a take, get real replies
• Arenas — Sports, Politics, Entertainment, News, Startups, Spirituality
• Live rooms — pick a side, argue now
• Human takes only. No AI slop.

No endless Reels feed inside the app.
Just say it. Prove it.

18+ only. By joining you agree to the Terms and Privacy Policy.

Join → leave your first take → https://barathx.com
```

Do **not** put rupee amounts or “get ₹150” on the public listing. Founding 100 public line only: spots are earned by opening a debate that gets real engagement.

---

## Screenshots

Play needs **at least 2 phone screenshots** (JPEG or 24-bit PNG, 16:9 to 9:16, 320–3840 px). Capture on a real Android phone after installing the internal build.

Shoot these five, in this order:

1. Landing / Join (phone OTP + Google, 18+ line visible)
2. Square feed with a real take
3. An Arena with Agree / Disagree sides
4. A reply thread
5. Profile (You)

How:

```
Open the internal-test install → go to the screen → Android screenshot
(Power + Volume down)
```

Then Play Console → Main store listing → Phone screenshots → upload.

Web screenshots of barathx.com are a fallback only. Prefer the real APK.

---

## After setup is complete: closed testing (required for Production)

New **personal** Play accounts (created after 13 Nov 2023) cannot ship Production until:

- App setup is finished
- A **closed** test is live
- **≥12 testers opted in continuously for 14 days**
- You click **Apply for production** on the Dashboard and answer the questionnaire

Internal testers do **not** automatically count. They must join the **closed** opt-in link.

### Start closed testing

1. Dashboard → Closed testing (unlocked once setup is done) → **Create release** (or Alpha track).
2. Promote the same AAB from Internal, or upload the current signed AAB again.
3. Release name: `0.1.2 (4)` to match `frontend/android/app/build.gradle`.
4. Release notes:

```
First closed test of BarathX. Sign up (18+), post a take on Square, pick a side in an Arena, try Live if a room is open. Report bugs to hello@barathx.com.
```

5. Testers tab → email list of **15–20 people** (buffer; Google counts 12 who stay opted in).
6. Countries: India + tester countries.
7. **Send for review**. Closed testing **is** reviewed. Wait until status is available to testers (often 1–7 days). The 14-day clock does **not** start on upload.
8. Share the **closed-test opt-in link**, not the internal one.

Tell testers: stay opted in for **14 days**, keep the app installed, open it a few times, leave one take. If the opted-in count drops below 12, the clock can reset.

### Apply for production (after day 14)

Dashboard → **Apply for production**. Draft answers:

**About your closed test**

- Recruited Campus Voices / friends / early BarathX users in India via WhatsApp and email.
- Testers used signup (phone OTP / Google), Square, Arenas, replies, profile, and Live when a room was open.
- Feedback collected on WhatsApp + Play testing feedback + hello@barathx.com.
- Summarize real bugs you fixed (login, feed, crash, OTP). Be specific.

**About your app**

- Target audience: Indian adults 18+, especially campus and Gen Z who want sided debate instead of a Reels feed.
- Value: text-first public square — pick a side, argue it live, human takes only.
- First-year installs: pick a conservative range (e.g. 10k–100k unless you have a stronger forecast).

**About production readiness**

- List changes made from tester feedback.
- Confirm 18+ age gate, privacy/terms URLs, no ads, login credentials provided for reviewers.

Google usually emails within ~7 days. Keep the closed test running until they approve.

---

## Tester invite

```
BarathX Android test — 2 minutes

1) On your Android phone, open this link while signed into the Gmail I added:
   [PASTE OPT-IN LINK]
2) Tap Become a tester → Download on Google Play → Install
3) Open BarathX → join (18+) with Google or phone OTP
4) Square → leave 1 take → open an Arena and pick a side
5) Stay installed for 2 weeks (closed test). Don’t opt out.

Stuck? The app will not show up if you only search Play. You must use the link first.
Bugs: screenshot + send to me, or hello@barathx.com
WhatsApp: https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o
```

Use the **internal** link today. After closed testing is approved, send the **closed** link to the same people (they must opt in again).

---

## What this repo cannot do for you

Play Console clicks, tester Gmails, the upload keystore, and reviewer login credentials stay outside git. Build/sign steps: [MOBILE.md](../../MOBILE.md). Product checklist: [SOFT-LAUNCH.md](./SOFT-LAUNCH.md).

---

## Quick order

1. **Today:** Internal opt-in link → testers install.
2. **Same day / this week:** Finish every “View tasks” item (listing + policy + data safety + reviewer login).
3. **Then:** Closed testing release → wait for Play review → 12 testers stay 14 days.
4. **Then:** Apply for production → when approved, promote the AAB to Production.
