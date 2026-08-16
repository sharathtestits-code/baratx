"""Block automated web/API scraping of BarathX content.

Stops common scraper User-Agents, empty bots, and bulk unauthenticated
polling. Browser SPA + mobile Capacitor + Google login still work.
"""

from __future__ import annotations

import re
from typing import Optional

from fastapi import Request
from starlette.responses import JSONResponse, Response

from app import rate_limit

# Known scrapers / headless harvesters (substring match on User-Agent).
_BLOCKED_UA = re.compile(
    r"("
    r"scrapy|beautifulsoup|bs4|httpx|python-requests|python-urllib|"
    r"aiohttp|libwww-perl|wget|curl/|httrack| mechanize|nutch|"
    r"phantomjs|headlesschrome|puppeteer|playwright|selenium|"
    r"bytespider|ccbot|gptbot|claudebot|anthropic-ai|chatgpt-user|"
    r"google-extended|perplexitybot|omgilibot|"
    r"diffbot|dataforseo|semrushbot|ahrefsbot|mj12bot|dotbot|"
    r"petalbot|baiduspider|sogou|exabot|"
    r"siteaudit|content-crawler|webscrap|crawl4ai|firecrawl|"
    r"node-fetch|go-http-client|java/|okhttp|apache-httpclient"
    r")",
    re.I,
)

# Allowlist: search + social link-preview agents (landing / OG only).
_ALLOWED_UA = re.compile(
    r"("
    r"googlebot|google-inspectiontool|bingbot|slurp|duckduckbot|"
    r"twitterbot|linkedinbot|whatsapp|telegrambot|facebookexternalhit|"
    r"barathx/|capacitor"
    r")",
    re.I,
)

# Paths that return bulk community content (scrape targets).
_SCRAPE_PATHS = re.compile(
    r"^/(posts|users|search|hashtags|communities|spaces|topics|feed)(/|$)",
    re.I,
)

# Static / health / auth should not be blocked by scraper UA (OAuth redirects, etc.)
_SKIP_PATHS = re.compile(
    r"^/(health|ready|version|media/|assets/|auth/|login|signup|docs|redoc|openapi)",
    re.I,
)


def client_user_agent(request: Request) -> str:
    return (request.headers.get("user-agent") or "").strip()


def is_scraper_ua(ua: str) -> bool:
    if not ua or len(ua) < 8:
        return True
    if _ALLOWED_UA.search(ua):
        return False
    return bool(_BLOCKED_UA.search(ua))


def is_bulk_scrape_path(path: str) -> bool:
    if _SKIP_PATHS.search(path or ""):
        return False
    return bool(_SCRAPE_PATHS.search(path or ""))


def has_browser_signal(request: Request) -> bool:
    """SPA / Capacitor clients usually send Accept: text/html or application/json + Origin."""
    accept = (request.headers.get("accept") or "").lower()
    origin = (request.headers.get("origin") or "").strip()
    referer = (request.headers.get("referer") or "").strip()
    if origin or referer:
        return True
    if "text/html" in accept:
        return True
    # Authenticated API clients (app) send Authorization
    if (request.headers.get("authorization") or "").strip():
        return True
    return False


def scrape_blocked_response() -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": "Automated scraping is not allowed on BarathX."},
        headers={
            "X-Robots-Tag": "noindex, nofollow, noai, noimageai",
            "Cache-Control": "no-store",
        },
    )


def enforce_anti_scrape(request: Request) -> Optional[Response]:
    """Return a 403 Response if this request looks like automated scraping."""
    path = request.url.path or "/"
    method = (request.method or "GET").upper()

    if method not in ("GET", "HEAD"):
        return None
    if not is_bulk_scrape_path(path):
        return None

    ua = client_user_agent(request)
    if is_scraper_ua(ua) and not has_browser_signal(request):
        return scrape_blocked_response()

    # Unauthenticated bulk polling: tight rate limit per IP.
    auth = (request.headers.get("authorization") or "").strip()
    if not auth:
        ip = rate_limit.client_ip(request)
        try:
            rate_limit.check_rate_limit(
                f"scrape:{ip}:{path.split('/')[1] if path.count('/') else 'root'}",
                limit=60,
                window_sec=60,
            )
        except ValueError:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Slow down."},
                headers={
                    "X-Robots-Tag": "noindex, nofollow, noai, noimageai",
                    "Retry-After": "60",
                },
            )
    return None


def robots_txt_body() -> str:
    """Strict robots policy: marketing shell ok for major engines; block scrapers + AI trainers."""
    return """# BarathX — human square. No scraping, no AI training crawls.
User-agent: *
Disallow: /admin
Disallow: /admin/
Disallow: /bx-ops
Disallow: /bx-ops/
Disallow: /posts
Disallow: /posts/
Disallow: /users
Disallow: /users/
Disallow: /search
Disallow: /hashtags
Disallow: /communities
Disallow: /spaces
Disallow: /topics
Disallow: /media/
Disallow: /api

User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: AhrefsBot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: DotBot
Disallow: /

User-agent: MJ12bot
Disallow: /

Sitemap: https://barathx.com/sitemap.xml
"""
