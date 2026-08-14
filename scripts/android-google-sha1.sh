#!/usr/bin/env bash
# Print Android signing SHA-1 values needed for Google Sign-In (Credential Manager).
# Register each SHA-1 on an Android OAuth client for package com.baratx.app
# in the same Google Cloud project as the Web client (VITE_GOOGLE_CLIENT_ID).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID="$ROOT/frontend/android"

echo "== Debug keystore SHA-1 (local APK / emulator) =="
if [[ -d "$ANDROID" ]]; then
  (cd "$ANDROID" && ./gradlew -q signingReport 2>/dev/null | sed -n '/Variant: debug/,/Variant:/p' | head -40) || {
    echo "Run from a machine with JDK + Android SDK:"
    echo "  cd frontend/android && ./gradlew signingReport"
  }
else
  echo "frontend/android missing"
fi

echo
echo "== Release / Play =="
echo "1) Upload-key SHA-1: keytool -list -v -keystore YOUR.jks -alias YOUR_ALIAS"
echo "2) Play App Signing SHA-1: Play Console → App integrity → App signing key certificate"
echo "Add BOTH to Google Cloud → Credentials → Android OAuth client (com.baratx.app)."
echo
echo "Web client ID (pass as webClientId / VITE_GOOGLE_CLIENT_ID) must stay the Web application client — never the Android client ID."
