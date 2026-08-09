/**
 * Host-aware OG / canonical URLs for Cloudflare Pages.
 * Same build can serve barathx.com and qa.barathx.com without VITE_PUBLIC_URL.
 */
export async function onRequest(context) {
  const response = await context.next();
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("text/html")) {
    return response;
  }

  const host = (context.request.headers.get("host") || "").toLowerCase();
  let origin = "https://barathx.com";
  if (host === "qa.barathx.com" || host.startsWith("qa.")) {
    origin = "https://qa.barathx.com";
  } else if (host.endsWith(".pages.dev")) {
    origin = `https://${host}`;
  }

  if (origin === "https://barathx.com") {
    return response;
  }

  const html = await response.text();
  const rewritten = html
    .replaceAll("https://barathx.com/", `${origin}/`)
    .replaceAll('content="https://barathx.com"', `content="${origin}"`);

  const headers = new Headers(response.headers);
  headers.delete("content-length");
  return new Response(rewritten, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
