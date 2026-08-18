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

## Unlock closed testing (the 11 dashboard tasks)

Dashboard → **Finish setting up your app → Provide app information and create your store listing**. Click each empty circle **top to bottom**. Until every task is done, **Closed testing stays locked**.

Work **Let us know about the content of your app** first (9 items), then **Manage how your app is organized and presented** (2 items).

### 1. Set privacy policy

- Privacy policy URL: `https://barathx.com/privacy`
- Save.

### 2. Sign in details

All or some of the app is behind login. Play reviewers **must** get in.

Before this form: on https://barathx.com create a dedicated **email + password** account (18+). Do **not** put 2FA / phone OTP on it. Use that email and password below.

- Are some parts of the app restricted? **Yes**
- Add instructions:

```
All core screens require sign-in (18+).

1. Open BarathX.
2. Tap Sign in.
3. Enter the email and password in this form.
4. Confirm you are 18+ if asked.
5. You land on Square. From the menu open an Arena, pick a side, post a take. Replies and Profile (You) are in the same signed-in app.

No one-time code, membership, or extra download is required for this account.
```

- Username / email: the reviewer account you created  
- Password: that account’s password  
- Other information required? **No**
- Save.

Do not leave this blank. Social apps get rejected if reviewers cannot log in.

### 3. Ads

- Does your app contain ads? **No, my app does not contain ads**
- Save.

### 4. Content rating

Start questionnaire → email `hello@barathx.com` → category **Social or Communication**.

**Social or Communication questionnaire (exact radios):**

| Question | Answer | Why |
|----------|--------|-----|
| Which best describes the app? | **Social** (Facebook / Twitter / Instagram type) | Public square, not 1:1 chat |
| Significant portion for dating or sexual relationships? | **No** | Debate product |
| Permit public sharing of nudity? | **No** | Guidelines forbid it |
| Permit public sharing of real-world graphic violence outside news? | **No** | Not a violence-sharing app |
| Share the user's current and precise physical location with other users? | **No** | Flip this if it is Yes. No location permission in the Android app |
| Allow users to purchase digital goods? | **No** | No IAP |
| Ability to block users or user-generated content? | **Yes** | Settings + profile mute/block |
| Ability to report users or user-generated content? | **Yes** | Post ··· → Report |
| Include chat moderation? | **Yes** | Live Talk filters, host remove, repeat reports auto-remove |
| Can interactions be limited to invited friends only? | **No** | Square is public. Following is a feed filter, not a private-friends lock |

Submit. When IARC emails the rating, **apply it to the app**. A Teen / 12+ rating is normal for public social UGC even though the product is 18+.

### 5. Target audience

- Age groups: tick **18 and over only**. Do **not** tick 13–15 or 16–17.
- Could the store listing appeal to children? **No**
- Not a Families app.
- Save.

### 6. Data safety

Overview:

| Question | Answer |
|----------|--------|
| Collects required user data types? | **Yes** |
| Encrypted in transit? | **Yes** |
| Independent security review / UPI verified? | Leave unchecked |

**Account creation (check only these three):**

- **Username and password** — email signup
- **Username and other authentication** — phone OTP
- **OAuth** — Google Sign-In

Uncheck **Username, password, and other authentication** (that is password plus extra auth on the same signup, which BarathX does not use). Leave **Other** and **does not allow accounts** unchecked.

**Delete account URL** (required):

```
https://barathx.com/privacy#account-deletion
```

**Delete some data without deleting the account?** **Yes**

**Delete data URL** (this is the red “Enter a valid URL” field — it is empty, so the form will not continue):

```
https://barathx.com/privacy#data-deletion
```

Both must start with `https://`. Do not paste an email address. If the hash URL is rejected, paste `https://barathx.com/privacy` in both fields.

The live privacy page already exists. After the latest copy is deployed, those anchors describe Settings → Delete account and post delete / email for partial data.

**Data types (this screen).** Click **Show** on each row. Target counts:

| Category | Tick | Do not tick |
|----------|------|-------------|
| Location | **None (0/2)** | Uncheck Approximate and Precise. IP is only used to rate-limit logins, not stored as a city/GPS |
| Personal info | **4/9:** Name, Email address, User IDs, Phone number | Address, Race and ethnicity, Political or religious beliefs, Sexual orientation, Other info |
| Financial info | 0/4 | All |
| Health and fitness | 0/2 | All |
| Messages | **1/3:** Other in-app messages | Emails, SMS or MMS |
| Photos and videos | **1/2:** Photos | Videos |
| Audio files | 0/3 | Live Talk is not saved as a recording |
| Files and docs | 0/1 | All |
| Calendar | 0/1 | All |
| Contacts | 0/1 | All (no address-book access; follows are not Contacts) |
| App activity | **2/5:** Other user-generated content; Other actions | App interactions, In-app search history, Installed apps |
| Web browsing | 0/1 | All |
| App info and performance | 0/3 | No crash SDK declared |
| Device or other IDs | **1/1** if the row is below the fold | — |

Political posts belong in **Other user-generated content**, not “Political or religious beliefs.” Beliefs is only if you store that as a profile field. BarathX does not.

If Location currently shows 1/2 and Personal info 7/9, open those rows and uncheck the extras before Next.

On the next step (usage), every ticked type is **Collected**, **not shared**. Showing a take on Square is not “shared” with a third party. Not sold. Encrypted in transit already answered Yes.

### 7. Government apps

- Is this a government app? **No**
- Save.

### 8. Financial features

- **My app doesn't provide any financial features**
- Founding 100 thank-you is not banking, payments, crypto, or an in-app purchase.
- Save.

### 9. Health

- **My app does not have any health features**
- Save.

### 10. Select an app category and provide contact details

This is Store settings, not the listing graphics.

- App or game: **App**
- Category: **Social**
- Email: `hello@barathx.com`
- Website: `https://barathx.com`
- Phone: optional
- Default language: English (India) if offered, else English (United States)
- Save.

### 11. Set up your store listing

Main store listing. Paste [§ Store listing copy](#store-listing-copy). Upload `brand/mobile/play-listing/`.

| Field | Value |
|-------|--------|
| App name | BarathX |
| Short description | India's public square — pick a side, argue it live. |
| Full description | See copy below |
| App icon | `play-listing/icon-512.png` (512×512) |
| Feature graphic | `play-listing/feature-1024x500.png` (1024×500) |
| Phone screenshots | At least **2** (aim for 5). Capture on a real phone — [§ Screenshots](#screenshots) |
| Privacy policy | already set in task 1 |

Tags if asked: debate, social, india, campus, news, sports.

This task stays incomplete until **icon + feature graphic + ≥2 phone screenshots** are uploaded.

### After the 11 are green

Closed testing unlocks on the same dashboard. When you create that closed release, include **India** plus every country a tester’s Google account is in. If a tester is abroad and India-only is selected, install fails.

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
