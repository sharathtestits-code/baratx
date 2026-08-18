# Play Console upload — BarathX 0.1.7

## Use this build (versionCode **9**)

| File | Use |
|------|-----|
| `barathx-0.1.7-release.aab` | **Upload this to Play Console** |
| `barathx-0.1.7-release.apk` | Sideload / direct install |

- package: `com.baratx.app`
- versionCode: **9**
- versionName: **0.1.7**

## Fixes in this build

- **Settings white screen** — `emailSaving` state crash fixed; Settings opens with Appearance themes
- **Android back** — system back leaves Settings (and other pages); on-screen **← Back** on Settings
- **Google Sign-In re-auth (error 16)** — clear stale Google session + retry; Capgo plugin bumped to **8.4.3**
- Landing / native consent dark card (no weird white 18+ boxes)
- Latest web UI synced into the Capacitor shell

## If Google Sign-In still fails on Play installs

Add **Play App Signing SHA-1** (Play Console → App integrity) as a separate Android OAuth client for `com.baratx.app` in the same Google Cloud project as the Web client. Also keep upload/release keystore SHA-1 registered. Email / phone OTP still work.
