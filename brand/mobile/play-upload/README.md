# Play Console upload — BarathX 0.1.3

Built for you to upload from Android Studio / Play Console.

## Files

| File | Use |
|------|-----|
| `barathx-0.1.3-release.aab` | **Play Console** → Production / Internal testing (preferred) |
| `barathx-0.1.3-release.apk` | Sideload / Internal app sharing / direct install |

Also copied to agent artifacts: `/opt/cursor/artifacts/play-console-upload/`

## What’s in this build

- **Native entry ≠ browser:** app opens `NativeLaunch` (phone-first), not marketing Landing  
- Google Sign-In scopes fix (Capgo)  
- Soft launch UI: Home · Square · Live · Arenas · You  
- versionCode **5** · versionName **0.1.3** · package `com.baratx.app`

## Upload steps (Play Console)

1. Play Console → your app → **Testing → Internal testing** (or Production when ready)  
2. **Create new release** → upload `barathx-0.1.3-release.aab`  
3. Release notes example:

```
Soft launch 0.1.3 — app home is phone-first (not the website). Google Sign-In fix. Square · Arenas · Live.
```

4. If Play asks for App Signing: keep using your **upload key** (`baratx-upload.jks` already used to sign this AAB).

## Android Studio

Open `frontend/android` → Build variants **release** → or just drag the AAB into Play Console.

## Note

Browser https://barathx.com still shows the marketing Landing. Only the **installed app** uses the new native launch screen.
