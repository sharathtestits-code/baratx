import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

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
  return {
    plugins: [react(), htmlPublicUrlPlugin(publicUrl)],
  };
});
