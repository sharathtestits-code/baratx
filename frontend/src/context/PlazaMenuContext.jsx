import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

/** Option B: menu starts collapsed; hamburger opens Change Arena drawer. */
const STORAGE_KEY = "bx_plaza_menu_open_v3";
const PlazaMenuContext = createContext(null);

function readStoredOpen() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "1") return true;
    if (stored === "0") return false;
  } catch {
    // ignore
  }
  return false;
}

export function PlazaMenuProvider({ children }) {
  const [open, setOpen] = useState(readStoredOpen);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, open ? "1" : "0");
    } catch {
      // ignore
    }
  }, [open]);

  const toggle = useCallback(() => {
    setOpen((v) => !v);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
  }, []);

  const value = useMemo(
    () => ({ open, setOpen, toggle, close }),
    [open, toggle, close]
  );

  return <PlazaMenuContext.Provider value={value}>{children}</PlazaMenuContext.Provider>;
}

export function usePlazaMenu() {
  const ctx = useContext(PlazaMenuContext);
  if (!ctx) {
    return { open: false, setOpen: () => {}, toggle: () => {}, close: () => {} };
  }
  return ctx;
}
