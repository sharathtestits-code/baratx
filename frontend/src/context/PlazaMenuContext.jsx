import { createContext, useCallback, useContext, useMemo, useState } from "react";

const PlazaMenuContext = createContext(null);

/**
 * Option B: menu starts closed. Hamburger opens Change Arena drawer.
 * Open state is not persisted — avoids stuck / half-open localStorage bugs.
 */
export function PlazaMenuProvider({ children }) {
  const [open, setOpen] = useState(false);

  const toggle = useCallback(() => {
    setOpen((v) => !v);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
  }, []);

  const openMenu = useCallback(() => {
    setOpen(true);
  }, []);

  const value = useMemo(
    () => ({ open, setOpen, toggle, close, openMenu }),
    [open, toggle, close, openMenu]
  );

  return <PlazaMenuContext.Provider value={value}>{children}</PlazaMenuContext.Provider>;
}

export function usePlazaMenu() {
  const ctx = useContext(PlazaMenuContext);
  if (!ctx) {
    return {
      open: false,
      setOpen: () => {},
      toggle: () => {},
      close: () => {},
      openMenu: () => {},
    };
  }
  return ctx;
}
