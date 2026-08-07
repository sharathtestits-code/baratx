import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "bx_plaza_menu_open";
const PlazaMenuContext = createContext(null);

export function PlazaMenuProvider({ children }) {
  const [open, setOpen] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === "1";
    } catch {
      return false;
    }
  });

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
