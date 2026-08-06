import { Capacitor } from "@capacitor/core";
import { App } from "@capacitor/app";
import { Keyboard } from "@capacitor/keyboard";
import { SplashScreen } from "@capacitor/splash-screen";
import { StatusBar, Style } from "@capacitor/status-bar";

/** True when running inside the native Capacitor shell (not mobile Safari). */
export function isNativeApp() {
  return Capacitor.isNativePlatform();
}

export function getNativePlatform() {
  return Capacitor.getPlatform(); // 'ios' | 'android' | 'web'
}

/**
 * Wire status bar, keyboard, splash, and Android back button.
 * Safe to call on web — no-ops when not native.
 */
export async function initNativeShell() {
  if (!isNativeApp()) return;

  document.documentElement.classList.add("native-app");
  document.documentElement.classList.add(`native-${getNativePlatform()}`);

  try {
    await StatusBar.setStyle({ style: Style.Dark });
    await StatusBar.setBackgroundColor({ color: "#FF671F" });
  } catch {
    // Some platforms (e.g. iOS edge cases) may reject style changes.
  }

  try {
    await SplashScreen.hide();
  } catch {
    // ignore
  }

  if (Capacitor.getPlatform() === "android") {
    App.addListener("backButton", ({ canGoBack }) => {
      if (canGoBack) {
        window.history.back();
      } else {
        App.exitApp();
      }
    });
  }

  try {
    Keyboard.addListener("keyboardWillShow", () => {
      document.documentElement.classList.add("keyboard-open");
    });
    Keyboard.addListener("keyboardWillHide", () => {
      document.documentElement.classList.remove("keyboard-open");
    });
  } catch {
    // Keyboard plugin optional on some builds
  }
}
