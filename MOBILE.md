# BaratX mobile apps (Capacitor)

BaratX Android + iOS ship as **Capacitor** shells around the existing Vite React app.

**Soft launch (Gen Z):** see **[brand/mobile/SOFT-LAUNCH.md](./brand/mobile/SOFT-LAUNCH.md)** — Android Internal testing first, then TestFlight.

| Item | Value |
|------|--------|
| App name | BaratX |
| Bundle / application id | `com.baratx.app` |
| Version | `0.1.0` (Android versionCode 2) |
| Web assets | `frontend/dist` (synced into native projects) |
| Production API | `https://baratx-production.up.railway.app` |
| Privacy | https://barathx.com/privacy |
| Terms | https://barathx.com/terms |

## Soft launch order (Gen Z India)

1. **Deploy** privacy/terms to production (`/privacy`, `/terms`).
2. **MSG91** real OTP on Railway (do not soft-launch on demo OTP).
3. **Android** Play Internal testing + Campus Voices (see `brand/mobile/SOFT-LAUNCH.md`).
4. **iOS** TestFlight after Android testers are live.
5. Keep acquisition on IG Reels → deep link to Play/TestFlight, not mobile browser.

Phone OTP is the primary auth for India Gen Z in-app. Google Sign-In is phase 2 (store OAuth clients).

---

## Prerequisites

- Node 20+ and npm
- **Android:** Android Studio (Giraffe+) with SDK 34+, JDK 17+
- **iOS:** macOS with Xcode 15+, Apple Developer Program membership
- Store accounts:
  - Google Play Console (~$25 one-time)
  - Apple Developer Program (~$99/year)

## Daily build workflow

```bash
cd frontend
npm install
npm run build:app          # vite build + cap sync
npm run open:android       # Android Studio
npm run open:ios           # Xcode (macOS only)
```

Useful scripts:

- `npm run build:app` — production web build + sync into `android/` and `ios/`
- `npm run cap:sync` — sync only (after `npm run build`)
- `npm run open:android` / `npm run open:ios`

## Auth in the native app

- **Phone OTP** and **email** work against the production API (same as web).
- **Google Sign-In** is intentionally gated in the native shell until you add Android/iOS OAuth clients in Google Cloud Console (package `com.baratx.app` + SHA-1 for Android; iOS client with reversed URL scheme). See “Google OAuth for stores” below.
- API CORS allows Capacitor origins: `https://localhost`, `capacitor://localhost`, `ionic://localhost`.

## Android → Play Store (AAB)

1. `cd frontend && npm run build:app && npm run open:android`
2. In Android Studio: wait for Gradle sync.
3. Create a release keystore (once):

   ```bash
   keytool -genkey -v -keystore baratx-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias baratx
   ```

   Store the `.jks` and passwords offline — never commit them.

4. Configure signing in `android/app` (Android Studio → Build → Generate Signed Bundle / APK), or add a local `keystore.properties` (gitignored).
5. **Build → Generate Signed Bundle / APK → Android App Bundle**.
6. Upload the `.aab` in Play Console → Production / Internal testing.
7. Store listing needs: title, short/full description, screenshots (phone), feature graphic, privacy policy URL (`https://barathx.com` privacy page when live).

### Debug APK (device / emulator)

```bash
cd frontend/android
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

## iOS → App Store

1. On a Mac: `cd frontend && npm run build:app && npm run open:ios`
2. In Xcode: select the **App** target → **Signing & Capabilities** → your Team.
3. Confirm Bundle Identifier `com.baratx.app`.
4. Set version / build numbers as needed.
5. Product → Archive → Distribute App → App Store Connect.
6. Complete App Store Connect metadata, screenshots, privacy nutrition labels, and age rating.

## Google OAuth for stores (phase 2)

Until this is done, the in-app Google button tells users to use phone/email.

1. Google Cloud Console → Credentials → create **Android** OAuth client:
   - Package name: `com.baratx.app`
   - SHA-1 from your release (and debug) keystore
2. Create **iOS** OAuth client with bundle id `com.baratx.app`.
3. Prefer `@codetrix-studio/capacitor-google-auth` or similar for native token → existing `/auth/google` `id_token` endpoint.
4. Keep the web GIS client for `barathx.com`.

## Icons & splash

- Android launchers: `frontend/android/app/src/main/res/mipmap-*`
- Splash: `drawable*/splash.png` + splash theme colors (`#FF671F`)
- iOS App Store icon: `ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png`

Regenerate after brand changes, then `npm run build:app`.

## What is / is not in this repo

**Included:** Capacitor config, `android/` + `ios/` projects, plugins (App, Keyboard, Splash, StatusBar), build scripts.

**Not included (you must do outside git):** Play / App Store submission, signing keys, paid developer accounts, push notifications (FCM/APNs), Universal Links / App Links.

## Smoke test checklist

After installing a debug build on a phone:

1. App opens to landing / auth
2. Phone OTP or email signup works against production API
3. Feed loads, post, follow, profile
4. Android back button navigates history then exits
5. Keyboard does not permanently hide the composer
