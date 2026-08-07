import { createContext, useContext, useEffect, useState } from "react";

const STORAGE_KEY = "bx_plaza_menu_open";
const PlazaMenuContext = createContext(null);

export function PlazaMenuProvider({ children }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, open ? "1" : "0");
    } catch {
      // ignore
    }
  }, [open]);

  function toggle() {
    setOpen((v) => !v);
  }

  function close() {
    setOpen(false);
  }

  return (
    <PlazaMenuContext.Provider value={{ open, setOpen, toggle, close }}>
      {children}
    </PlazaMenuContext.Provider>
  );
}

export function usePlazaMenu() {
  const ctx = useContext(PlazaMenuContext);
  if (!ctx) {
    return { open: false, setOpen: () => {}, toggle: () => {}, close: () => {} };
  }
  return ctx;
}
