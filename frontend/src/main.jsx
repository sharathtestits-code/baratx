import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { initThemeFromStorage } from "./theme.js";
import { applyDocumentLanguage, getStoredLanguage } from "./i18n.js";
import { initNativeShell } from "./native.js";
import "./index.css";

initThemeFromStorage();
applyDocumentLanguage(getStoredLanguage());
initNativeShell();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
