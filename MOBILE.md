# BarathX mobile apps (Capacitor)

BarathX Android + iOS ship as **Capacitor** shells around the existing Vite React app.

**Soft launch (Gen Z):** see **[brand/mobile/SOFT-LAUNCH.md](./brand/mobile/SOFT-LAUNCH.md)** — Android Internal testing first, then TestFlight.

| Item | Value |
|------|--------|
| App name | BarathX |
| Bundle / application id | `com.baratx.app` |
| Version | `0.1.2` (Android versionCode 4) |
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

Phone OTP remains a primary path for India Gen Z. **Native Google Sign-In is wired** (`@capgo/capacitor-social-login`) — finish Google Cloud Android/iOS clients (below) so the live button works on device.

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
- **Google Sign-In** uses `@capgo/capacitor-social-login` on Android/iOS and Google Identity Services on web. Native login sends an ID token to `POST /auth/google` (same as web).
- **Android live checklist:** Web client ID in the app build + Android OAuth client (`com.baratx.app` + SHA-1) in the **same** Google Cloud project. See “Google OAuth for stores” below.
- **iOS:** also needs an iOS OAuth client, `VITE_GOOGLE_IOS_CLIENT_ID`, and the reversed client ID URL scheme in `Info.plist`.
- API CORS allows Capacitor origins: `https://localhost`, `capacitor://localhost`, `ionic://localhost`.
- API `GOOGLE_CLIENT_ID` must be the **Web** client ID (ID token audience). Optional `GOOGLE_CLIENT_IDS` for extra audiences.

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

## Google OAuth for stores (required for native Google)

The app already calls native Google Sign-In. Until Cloud Console matches your signing keys, Android shows an error like `[28444] Developer console is not set up correctly` — use phone OTP meanwhile.

### 1) Same Google Cloud project as web

You already have a **Web application** client (used as `VITE_GOOGLE_CLIENT_ID` / Railway `GOOGLE_CLIENT_ID`). Keep that ID — native Android passes it as `webClientId`. **Do not** put an Android client ID in `VITE_GOOGLE_CLIENT_ID`.

### 2) Android OAuth client(s)

1. [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) → **Create credentials → OAuth client ID → Android**
2. Package name: `com.baratx.app`
3. SHA-1: print with `./scripts/android-google-sha1.sh` or:

   ```bash
   cd frontend/android && ./gradlew signingReport
   ```

   Register **debug** SHA-1 for local APKs, **release/upload** SHA-1 for signed builds, and **Play App Signing** SHA-1 from Play Console → App integrity (for Internal testing / Production).

4. OAuth consent screen: **External**. If status is Testing, add every tester Gmail under **Test users**.
5. Rebuild the app after console changes (propagation can take a while):

   ```bash
   cd frontend && npm run build:app
   ```

### 3) iOS OAuth client (when shipping TestFlight)

1. Create **iOS** OAuth client, bundle id `com.baratx.app`.
2. Set `VITE_GOOGLE_IOS_CLIENT_ID` in the app build env.
3. In `ios/App/App/Info.plist` add URL scheme = **reversed** iOS client ID  
   (`123-abc.apps.googleusercontent.com` → `com.googleusercontent.apps.123-abc`).
4. Optional: set Railway `GOOGLE_CLIENT_IDS` to the iOS client if tokens are not minted with `iOSServerClientId` = web.

### 4) Smoke test

1. Install a fresh APK signed with a SHA-1 you registered.
2. Landing / Login → **Continue with Google** → pick account → land on Square.
3. If it fails, Logcat filter `GoogleProvider` — confirm `package`, `signingSha1`, `webClientId`.

Plugin: `@capgo/capacitor-social-login` (Capacitor 8). Providers other than Google are disabled in `capacitor.config.json` to keep APK size down.

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
