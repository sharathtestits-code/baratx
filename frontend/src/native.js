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

const THEME_BAR = {
  midnight: { color: "#0D0D12", style: Style.Dark },
  saffron: { color: "#FF671F", style: Style.Light },
  monsoon: { color: "#0d9488", style: Style.Light },
  ink: { color: "#000080", style: Style.Light },
};

/** Keep native status bar aligned with the active appearance theme. */
export async function syncNativeChrome(themeId = "midnight") {
  if (!isNativeApp()) return;
  const conf = THEME_BAR[themeId] || THEME_BAR.midnight;
  try {
    await StatusBar.setStyle({ style: conf.style });
    await StatusBar.setBackgroundColor({ color: conf.color });
  } catch {
    // Some platforms may reject style changes.
  }
}

/**
 * Wire status bar, keyboard, splash, and Android back button.
 * Safe to call on web — no-ops when not native.
 */
export async function initNativeShell() {
  if (!isNativeApp()) return;

  document.documentElement.classList.add("native-app");
  document.documentElement.classList.add(`native-${getNativePlatform()}`);

  const stored =
    typeof localStorage !== "undefined" ? localStorage.getItem("bx_theme") || "midnight" : "midnight";
  await syncNativeChrome(stored);

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
