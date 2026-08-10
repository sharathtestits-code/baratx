import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function readMvpVersion() {
  if (process.env.VITE_MVP_VERSION && /^\d+$/.test(String(process.env.VITE_MVP_VERSION).trim())) {
    return String(process.env.VITE_MVP_VERSION).trim();
  }
  try {
    const n = readFileSync(resolve(repoRoot, "VERSION"), "utf8").trim();
    return /^\d+$/.test(n) ? n : "1";
  } catch {
    return "1";
  }
}

/**
 * Inject environment-specific OG / canonical URLs into index.html.
 * Set VITE_PUBLIC_URL=https://qa.barathx.com for QA builds (Cloudflare Pages).
 * Defaults to production https://barathx.com.
 */
function htmlPublicUrlPlugin(publicUrl) {
  const origin = (publicUrl || "https://barathx.com").replace(/\/$/, "");
  return {
    name: "html-public-url",
    transformIndexHtml(html) {
      return html
        .replaceAll("https://barathx.com/", `${origin}/`)
        .replaceAll('content="https://barathx.com"', `content="${origin}"`);
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const publicUrl = env.VITE_PUBLIC_URL || "https://barathx.com";
  const mvp = readMvpVersion();
  process.env.VITE_MVP_VERSION = mvp;
  return {
    plugins: [react(), htmlPublicUrlPlugin(publicUrl)],
    define: {
      "import.meta.env.VITE_MVP_VERSION": JSON.stringify(mvp),
    },
  };
});
