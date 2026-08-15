import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
import {
  applyDocumentLanguage,
  getStoredLanguage,
  localeMeta,
  normalizeLanguage,
  translate,
} from "../i18n";

const LocaleContext = createContext({
  language: "en",
  locale: localeMeta("en"),
  setLanguage: () => {},
  t: (key) => key,
});

export function LocaleProvider({ children }) {
  const { user } = useAuth();
  const [language, setLanguageState] = useState(() =>
    normalizeLanguage(user?.language || getStoredLanguage())
  );

  useEffect(() => {
    if (user?.language) {
      const next = applyDocumentLanguage(user.language);
      setLanguageState(next);
    }
  }, [user?.language]);

  const setLanguage = useCallback((next) => {
    const id = applyDocumentLanguage(next);
    setLanguageState(id);
    return id;
  }, []);

  const t = useCallback(
    (key, vars) => translate(language, key, vars),
    [language]
  );

  const value = useMemo(
    () => ({
      language,
      locale: localeMeta(language),
      setLanguage,
      t,
    }),
    [language, setLanguage, t]
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  return useContext(LocaleContext);
}

export function useT() {
  return useLocale().t;
}
