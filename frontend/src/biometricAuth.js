/**
 * Biometric unlock (Face ID / Touch ID / Android fingerprint).
 *
 * Flow:
 * 1. After successful login, offer to enable biometric unlock.
 * 2. If enabled, store the JWT in the OS secure store (Keychain / Keystore).
 * 3. On next app open, prompt Face ID / fingerprint → auto-login with the
 *    stored token (no re-enter password).
 *
 * Plugin: @capgo/capacitor-native-biometric (Capacitor 8, v8.6+).
 */

import { NativeBiometric, BiometryType } from "@capgo/capacitor-native-biometric";
import { isNativeApp } from "./native";

const SERVER = "com.baratx.app";
const PREF_KEY = "bx_biometric_enabled";

export function biometricLabel(type) {
  switch (type) {
    case BiometryType.FACE_ID:
      return "Face ID";
    case BiometryType.TOUCH_ID:
      return "Touch ID";
    case BiometryType.FINGERPRINT:
      return "Fingerprint";
    case BiometryType.FACE_AUTHENTICATION:
      return "Face unlock";
    default:
      return "Biometric unlock";
  }
}

export async function isBiometricAvailable() {
  if (!isNativeApp()) return { available: false, type: BiometryType.NONE };
  try {
    const result = await NativeBiometric.isAvailable();
    return {
      available: result.isAvailable,
      type: result.biometryType,
      label: biometricLabel(result.biometryType),
    };
  } catch {
    return { available: false, type: BiometryType.NONE };
  }
}

export function isBiometricEnabled() {
  try {
    return localStorage.getItem(PREF_KEY) === "1";
  } catch {
    return false;
  }
}

export async function enableBiometric(token, username) {
  await NativeBiometric.verifyIdentity({
    reason: "Enable biometric unlock for BarathX",
    title: "BarathX",
    subtitle: "Verify to enable quick unlock",
    maxAttempts: 3,
  });
  await NativeBiometric.setCredentials({
    server: SERVER,
    username: username || "barathx-user",
    password: token,
  });
  localStorage.setItem(PREF_KEY, "1");
}

export async function disableBiometric() {
  localStorage.removeItem(PREF_KEY);
  try {
    await NativeBiometric.deleteCredentials({ server: SERVER });
  } catch {
    // credentials may not exist
  }
}

export async function biometricLogin() {
  await NativeBiometric.verifyIdentity({
    reason: "Unlock BarathX",
    title: "BarathX",
    subtitle: "Use Face ID or fingerprint to sign in",
    maxAttempts: 3,
  });
  const creds = await NativeBiometric.getCredentials({ server: SERVER });
  if (!creds?.password) {
    throw new Error("No saved session found. Please sign in again.");
  }
  return creds.password; // the stored JWT
}

export async function hasSavedCredentials() {
  if (!isNativeApp()) return false;
  try {
    const result = await NativeBiometric.isCredentialsSaved({ server: SERVER });
    return result.hasSavedCredentials;
  } catch {
    return false;
  }
}
