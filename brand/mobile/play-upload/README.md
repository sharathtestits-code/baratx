# Play Console upload — BarathX 0.1.8

## Use this build (versionCode **10**)

| File | Use |
|------|-----|
| `barathx-0.1.8-release.aab` | **Upload this to Play Console** |
| `barathx-0.1.8-release.apk` | Sideload / direct install |

- package: `com.baratx.app`
- versionCode: **10**
- versionName: **0.1.8**

## Fixes in this build

- **Google Sign-In browser fallback** — if native Credential Manager fails (error 16 / re-auth), opens `barathx.com/native-google-auth` (Web Google client), then returns via `barathx://google-auth`
- Explicit **Continue with Google in browser** button on native login
- Deep-link intent filter for `barathx://google-auth`
- Prior 0.1.7 fixes retained (Settings crash, Android back, Capgo 8.4.3)

## Deploy note

Ship the website update with `/native-google-auth` **before or with** this Play build so the browser fallback page is live.

## If native Google still fails

Still register **Play App Signing** SHA-1(s) (Classical + post-quantum if shown) as Android OAuth clients for `com.baratx.app`. Browser fallback works without those SHA-1s.
