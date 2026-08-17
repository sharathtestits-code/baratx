# What you need to get BarathX on the iOS App Store

Updated: **2026-08-17**

This is the Product Manager checklist. The Capacitor iOS shell already lives in
`frontend/ios/` (bundle id `com.baratx.app`). Apple will not accept a git repo.
You still do accounts, signing, screenshots, and App Store Connect on a Mac.

**Soft-launch order:** Android testers first (`SOFT-LAUNCH.md`), then iOS
TestFlight, then public App Store.

---

## 1. You must do (cannot be done from this repo)

| # | Item | Why Apple needs it | Status |
|---|------|--------------------|--------|
| 1 | **Apple Developer Program** ($99/year) at [developer.apple.com/programs](https://developer.apple.com/programs) | Required to create App IDs, certificates, TestFlight, and the store listing | You |
| 2 | **A Mac with Xcode 16+** | iOS archives only build on macOS | You |
| 3 | **App Store Connect app record** | Create app: name **BarathX**, bundle id `com.baratx.app`, SKU `barathx-ios`, primary language English | You |
| 4 | **Signing Team** in Xcode | Target **App** → Signing & Capabilities → your Team, Automatic signing | You |
| 5 | **Privacy Policy live** | `https://barathx.com/privacy` must load (also `/terms`) | Confirm after deploy |
| 6 | **Real SMS OTP (MSG91)** | Reviewers and testers must complete signup. Demo OTP in the API response will fail review | Railway env |
| 7 | **6.9" iPhone screenshots** (at least 1, aim for 5) | Required size class. Portrait **1320×2868** (also accepts 1290×2796 or 1260×2736). PNG/JPEG, no transparency | You, from Simulator or device |
| 8 | **App Privacy (nutrition labels)** in App Store Connect | Match the table in section 5 below | You |
| 9 | **Age rating questionnaire** | BarathX is 18+ UGC / debate. Expect **17+** | You |
| 10 | **Review notes + demo account** | Reviewer must sign in. Phone OTP is painful for Apple. Give **email + password** (and confirm the account is 18+) | You |
| 11 | **Support URL + marketing URL** | Support: `https://barathx.com` (or a contact page). Marketing: `https://barathx.com` | You |
| 12 | **Contact email** | `hello@barathx.com` | You |

Do **not** wait for public Production to start TestFlight. Internal testers can
install the same build Apple later reviews.

---

## 2. Already in the repo

- Capacitor iOS project, display name **BarathX**, bundle id `com.baratx.app`
- 1024×1024 App Store icon (`AppIcon-1024.png`, orange BX mark)
- Phone OTP + email signup, in-app **Delete account** (Settings)
- Report post, mute, block
- Privacy + Terms pages
- Camera / photo / microphone usage strings (Live Talk + image posts)
- Privacy manifest `PrivacyInfo.xcprivacy`
- Export compliance flag `ITSAppUsesNonExemptEncryption = false` (HTTPS only)
- iPhone-only target (skips iPad screenshots on the first listing)
- Native shell **does not** say “App Store coming soon” (that copy would fail review)
- Google Sign-In is **hidden on iOS** until Sign in with Apple ships (guideline **4.8**)

---

## 3. Hard Apple rules for this product

### 4.8 Sign in with Apple (blocker if Google stays)

If the iOS app shows **Continue with Google**, Apple **requires** Sign in with
Apple as an equivalent option.

**First listing path (done in code):** hide Google on iOS. Users join with
**phone OTP** (India primary) or **email**. Web and Android keep Google.

**Later:** add Sign in with Apple (Apple capability + backend token verify +
button), then turn Google back on for iOS. See `IOS_SIGN_IN_WITH_APPLE_READY`
in `frontend/src/nativeGoogleAuth.js`.

### 5.1.1(v) Account deletion

Apps that create accounts must let the user delete the account **in the app**.
Settings → Privacy & security → **Delete my account** (type `DELETE`). Keep this
easy to find. Privacy Policy now points here, not only “email us”.

### 1.2 User-generated content

Required and present: report, block/mute, published content rules, a way to
contact us. Review notes should mention: post `···` → Report, Settings → Blocked,
`/guidelines`.

### 4.2 Minimum functionality

This is a Capacitor (web-in-native) app. Reviewers reject “just a website”
wrappers. Mitigations already in place: local bundled UI (not a remote Safari
tab), native splash/status bar, phone OTP, Live Talk camera/mic, in-app account
deletion. **Do not** point WKWebView at `https://barathx.com` as the only UI.

In the store listing, never say “open in browser” as the product. The app **is**
the product.

### 5.1.2 Privacy nutrition labels

Must match what the app actually collects. Use section 5. If you add analytics
or ads later, update both App Store Connect **and** `PrivacyInfo.xcprivacy`.

---

## 4. Build and upload (Mac)

```bash
cd frontend
npm install
npm run build:app          # production API + cap sync
npm run open:ios           # opens Xcode
```

In Xcode:

1. Select the **App** target → **Signing & Capabilities** → Team.
2. Confirm Bundle Identifier `com.baratx.app`.
3. Version **1.0** (marketing), Build **1** (bump build for every upload).
4. Destination: **Any iOS Device (arm64)**.
5. **Product → Archive** → **Distribute App** → **App Store Connect** → Upload.
6. Wait for processing in App Store Connect (email + activity tab).
7. Enable **TestFlight** → add yourself + Campus Voices by email.
8. When TestFlight is stable: add the listing, screenshots, privacy, then
   **Submit for Review**.

Each new upload needs a **higher build number** (`CURRENT_PROJECT_VERSION`).
Version `1.0` can stay until you ship a user-facing update.

### Google OAuth (only after Sign in with Apple)

If you re-enable Google on iOS:

1. Google Cloud → iOS OAuth client, bundle id `com.baratx.app`.
2. Set `VITE_GOOGLE_IOS_CLIENT_ID` at `npm run build:app` time.
3. In `Info.plist`, add URL scheme = **reversed** iOS client ID
   (`123-abc.apps.googleusercontent.com` → `com.googleusercontent.apps.123-abc`).
4. Set `IOS_SIGN_IN_WITH_APPLE_READY` to `true` only when the Apple button is live.

---

## 5. App Store Connect — paste-ready listing

**Name:** BarathX  
**Subtitle (≤30 chars):** India’s public square  
**Category:** Social Networking  
**Secondary:** News  
**Age:** 17+ (complete the questionnaire; 18+ in Terms)  
**Copyright:** 2026 BarathX  
**Support URL:** https://barathx.com  
**Marketing URL:** https://barathx.com  
**Privacy Policy URL:** https://barathx.com/privacy  
**Contact:** hello@barathx.com

**Promotional text (optional, 170 chars, editable without review):**

```
India’s public square. Short posts, real sides, live debate. Pick a side. Argue it.
```

**Description:**

```
BarathX is India’s public square.

Short posts. Real sides. Real debate.

• Square — drop a take, get real replies
• Arenas — Sports, Politics, Entertainment, News, Startups, Spirituality
• Live rooms — pick a side, argue now (optional Live Talk audio)
• Human takes only. No AI slop.

No endless Reels feed inside the app.
Just say it. Prove it.

18+ only. Join with your phone or email.

barathx.com
```

**Keywords (100 chars, comma-separated, no spaces after commas is fine):**

```
debate,India,social,campus,politics,sports,news,startups,public square,BarathX
```

**What's New (1.0):**

```
First App Store release. Square, Arenas, Live rooms, phone or email signup.
```

### Screenshots (phone, 6.9" portrait)

Capture from iPhone 16 Pro Max Simulator (or 15 Pro Max at 1290×2796).

1. Landing / join (phone OTP) — no “coming soon”
2. Square feed with a real take
3. Arena with Agree / Disagree sides
4. Reply thread
5. Profile or Live room

Do not include the status bar with a 0% battery, placeholder lorem, or browser
chrome. Use real (or clearly demo) India-relevant posts.

### App Privacy answers (nutrition labels)

No tracking. No third-party advertising. Data used to run the account and feed.

| Data type | Collected | Linked to identity | Used for tracking | Purpose |
|-----------|-----------|--------------------|-------------------|---------|
| Name | Yes | Yes | No | App Functionality |
| Email Address | Yes | Yes | No | App Functionality |
| Phone Number | Yes | Yes | No | App Functionality |
| User ID | Yes | Yes | No | App Functionality |
| Photos | Yes (optional uploads) | Yes | No | App Functionality |
| User Content (posts, replies) | Yes | Yes | No | App Functionality |
| Product Interaction | Yes | Yes | No | App Functionality |
| Audio Data | Yes (Live Talk, on-device / peers) | Yes | No | App Functionality |
| Customer Support | Optional via email | Yes | No | App Functionality |

Not collected: precise location, contacts, browsing history, advertising data.

### Age rating (typical answers)

- Unrestricted web access: **No** (in-app UGC, not a full Safari browser)
- User-generated content: **Frequent / Intense**
- Mature / suggestive themes: **Infrequent** (debate can include politics)
- Profanity: **Infrequent**
- Horror / violence / gambling / alcohol / medical: **None** unless you later add them
- 17+ is the expected result. Terms already require 18+.

### Review notes (paste into App Review Information)

```
BarathX is a social debate app for India (18+).

Demo account (email):
  email: review@barathx.com
  password: (set a strong password and keep this account alive)

How to review:
1. Open the app → Join with the demo email (or Phone OTP if you prefer).
2. Complete first take on Square.
3. Open an Arena, pick Agree or Disagree, post a reply.
4. Report: any post → ··· → Report.
5. Delete account: You → Settings → Privacy & security → type DELETE.

Live Talk uses microphone (and camera if the user turns video on).
We do not use Sign in with Google on iOS yet (phone + email only) so Sign in
with Apple is not required for this build.

Privacy: https://barathx.com/privacy
Terms: https://barathx.com/terms
Guidelines: https://barathx.com/guidelines
Contact: hello@barathx.com
```

Create `review@barathx.com` (or another inbox you control) **before** submit.
Do not give Apple a phone-only path with no backup login.

---

## 6. Export compliance

The app only uses HTTPS (standard encryption). In App Store Connect, answer:

- **Does this app use encryption?** Yes (HTTPS)
- **Exempt?** Yes → ITSAppUsesNonExemptEncryption is already `false` in Info.plist
  so you should not need to answer this on every upload.

If Apple still asks: France encryption declaration is not required for HTTPS-only.

---

## 7. What will get you rejected (avoid)

| Risk | Fix |
|------|-----|
| Google button without Sign in with Apple | Keep Google hidden on iOS until Apple Sign-In is live |
| Landing still says “App Store coming soon” | Native copy is already switched off in this app shell |
| Broken signup (demo OTP / no SMS) | Turn on MSG91 on Railway; give reviewers email login |
| Privacy URL 404 | Deploy `/privacy` and `/terms` to barathx.com |
| No in-app account deletion | Already in Settings; do not bury or remove it |
| Empty feed / crash on launch | Seed Square with real posts; TestFlight smoke test first |
| iPad listing with stretched iPhone UI | First ship is **iPhone only** |
| Placeholder / alpha App Icon | 1024 icon must be opaque PNG; no rounded corners drawn in |
| Reviewer cannot log in | Demo email + password in Review Notes |

---

## 8. After you are live

1. Replace website “App Store · Coming soon” with the real store URL
   (`https://apps.apple.com/app/idXXXXXXXX`).
2. Deep link IG / WhatsApp campaigns to the store, not mobile Safari.
3. Plan Sign in with Apple if you want Google on iOS.
4. Universal Links (`applinks:barathx.com`) are optional and not in this repo.

Contact for store questions: hello@barathx.com
