/**
 * Prod release label from VITE_MVP_VERSION (set at build from repo VERSION).
 * Auto-bumps on each push to `main` — see .github/workflows/bump-mvp.yml.
 */
export function mvpNumber() {
  const n = String(import.meta.env.VITE_MVP_VERSION || "1").trim();
  return /^\d+$/.test(n) ? n : "1";
}

export function mvpLabel() {
  return `MVP${mvpNumber()}`;
}
