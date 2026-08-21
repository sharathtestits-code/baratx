# Create Android Google auth (copy-paste)

You create this in **your** Google Cloud project (agents cannot click Console for you).

**Project:** BaratX (`682923055091`)  
**Open:** https://console.cloud.google.com/apis/credentials?project=682923055091  

Must be the **same** project as Web client  
`682923055091-imk39450dk207psnoetvhnvseslvq0qp.apps.googleusercontent.com`

---

## Generate / create one — Upload key (required)

1. **Create credentials** → **OAuth client ID**
2. Application type: **Android**
3. Paste:

| Field | Value |
|-------|--------|
| Name | `BarathX Android upload` |
| Package name | `com.baratx.app` |
| SHA-1 | `4A:4A:63:80:D4:20:9B:6A:1D:FD:DA:7E:BE:8B:22:FC:71:EC:B2:AA` |

4. **Create**

Do **not** put this Android client ID into `VITE_GOOGLE_CLIENT_ID` (keep the Web client).

---

## Create more (Play installs — error 16)

Play Console → **App integrity** → App signing key certificate.

Create **separate** Android OAuth clients (same package `com.baratx.app`) for each SHA-1 shown:

- Classical App signing SHA-1  
- Post-quantum App signing SHA-1 (if listed)

Name them e.g. `BarathX Android Play classical` / `BarathX Android Play PQ`.

---

## Consent / test users

1. OAuth consent screen → **External**
2. If status is **Testing**, add your phone Gmail (and any tester) under **Test users**
3. Wait up to a few hours after creating clients, then uninstall + reinstall the Play build

---

## Browser auth (works without Play SHA-1)

Ship **0.1.8** + deploy site route `/native-google-auth` (PR #103).  
App → **Continue with Google in browser** uses the Web client only.

---

## Fingerprints on file

| Key | SHA-1 |
|-----|--------|
| Upload / release (`baratx` jks) | `4A:4A:63:80:D4:20:9B:6A:1D:FD:DA:7E:BE:8B:22:FC:71:EC:B2:AA` |
| Debug (local only; this cloud VM) | `43:9A:73:E4:D8:88:31:B3:0A:CF:04:09:23:F5:2C:A6:91:EF:2B:3B` |
