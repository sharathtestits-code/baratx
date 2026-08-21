# Soft launch — what works (lock this in)

**Verified 2026-08-18 (Sharath):** sideload APK + **phone OTP** works. Do not block soft launch on Google / Play SHA-1 / Studio verify loops.

## Ship path (use this)

1. Build APK → `brand/mobile/play-upload/barathx-latest-release.apk` (+ versioned copy)
2. Push to **main** (so GitHub raw + `/get-app` stay current)
3. Testers: uninstall Play build → install from https://barathx.com/get-app/ or GitHub raw APK
4. Login: **Continue with phone** (OTP)

## Do not prioritize (until Cloud Console access is fixed)

- Native Google Sign-In / Play App Signing SHA-1 OAuth clients
- Waiting on Play Internal testing “verification” for every build

## Daily reminder

Morning daily-pack email nudges once:

1. Paste **WhatsApp + X + LinkedIn** (pack copy includes get-app)
2. Push `barathx-latest-release.apk` to main if you shipped app changes
3. Soft launch login = phone OTP — not Google/Play SHA-1

Owner: `sharathtestits@gmail.com`
