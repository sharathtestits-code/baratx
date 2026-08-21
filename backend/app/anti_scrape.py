"""Block automated web/API scraping of BarathX content.

Covers:
- Classic API harvesters (Scrapy, curl, GPTBot, …)
- Headless browser scroll scrapers (Puppeteer/Playwright/Selenium)
- Rapid infinite-scroll pagination without the official web/native client header

Real SPA + Capacitor still work (they send X-BarathX-Client).
"""

from __future__ import annotations

import re
from typing import Optional

from fastapi import Request
from starlette.responses import JSONResponse, Response

from app import rate_limit

CLIENT_HEADER = "x-barathx-client"
VALID_CLIENTS = frozenset({"web", "native"})

# Known scrapers / headless harvesters (substring match on User-Agent).
_BLOCKED_UA = re.compile(
    r"("
    r"scrapy|beautifulsoup|bs4|httpx|python-requests|python-urllib|"
    r"aiohttp|libwww-perl|wget|curl/|httrack|mechanize|nutch|"
    r"phantomjs|headlesschrome|headless|puppeteer|playwright|selenium|"
    r"chromedriver|geckodriver|webdriver|"
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

# Paths that return bulk community content (scrape / scroll targets).
_SCRAPE_PATHS = re.compile(
    r"^/(posts|users|search|trending|hashtags|communities|spaces|topics|feed)(/|$)",
    re.I,
)

# Static / health / auth should not be blocked by scraper UA (OAuth redirects, etc.)
_SKIP_PATHS = re.compile(
    r"^/(health|ready|version|media/|assets/|auth/|login|signup|docs|redoc|openapi|robots\.txt)",
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


def has_official_client(request: Request) -> bool:
    """SPA and native shells send X-BarathX-Client: web|native."""
    raw = (request.headers.get(CLIENT_HEADER) or "").strip().lower()
    return raw in VALID_CLIENTS


def is_scroll_page(request: Request) -> bool:
    """True when this looks like infinite-scroll / cursor pagination."""
    q = request.query_params
    return any(q.get(k) for k in ("before", "cursor", "offset", "page", "after"))


def has_browser_signal(request: Request) -> bool:
    """SPA / Capacitor clients usually send Origin/Referer or Authorization."""
    if has_official_client(request):
        return True
    origin = (request.headers.get("origin") or "").strip()
    referer = (request.headers.get("referer") or "").strip()
    if origin or referer:
        return True
    accept = (request.headers.get("accept") or "").lower()
    if "text/html" in accept:
        return True
    if (request.headers.get("authorization") or "").strip():
        return True
    return False


def scrape_blocked_response(detail: str = "Automated scraping is not allowed on BarathX.") -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": detail},
        headers={
            "X-Robots-Tag": "noindex, nofollow, noai, noimageai",
            "Cache-Control": "no-store",
        },
    )


def rate_limited_response() -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Slow down."},
        headers={
            "X-Robots-Tag": "noindex, nofollow, noai, noimageai",
            "Retry-After": "60",
        },
    )


def is_native_http_ua(ua: str) -> bool:
    """Capacitor / Android HTTP stacks (not headless browser scrapers)."""
    low = (ua or "").lower()
    if "headless" in low or "playwright" in low or "puppeteer" in low or "selenium" in low:
        return False
    return bool(
        re.search(r"okhttp|capacitor|dalvik|;\s*wv\)|barathx/", low)
        or re.search(r"^java/", low)
    )


def enforce_anti_scrape(request: Request) -> Optional[Response]:
    """Return a 403/429 Response if this request looks like automated scraping."""
    path = request.url.path or "/"
    method = (request.method or "GET").upper()

    if method not in ("GET", "HEAD"):
        return None
    if not is_bulk_scrape_path(path):
        return None

    ua = client_user_agent(request)
    official = has_official_client(request)
    # Always block known scraper / headless UAs — Origin spoofing must not bypass.
    # Official native shells may send OkHttp/Java UAs; allow those with the client header.
    if is_scraper_ua(ua) and not _ALLOWED_UA.search(ua):
        if not (official and is_native_http_ua(ua)):
            return scrape_blocked_response()

    scrolling = is_scroll_page(request)

    # Infinite-scroll harvest without the real web/native client header.
    if scrolling and not official and not _ALLOWED_UA.search(ua):
        return scrape_blocked_response(
            "Web scroll scraping is not allowed. Open BarathX in a browser."
        )

    # Unauthenticated bulk / scroll polling: tighter when scrolling or missing client.
    auth = (request.headers.get("authorization") or "").strip()
    ip = rate_limit.client_ip(request)
    bucket_root = path.strip("/").split("/")[0] if path.strip("/") else "root"

    if scrolling:
        # Scroll pagination is the main web-scraper pattern.
        limit, window = (45, 60) if (auth and official) else (18, 60)
        bucket = f"scroll:{ip}:{bucket_root}"
    elif not auth:
        limit, window = (40, 60) if official else (20, 60)
        bucket = f"scrape:{ip}:{bucket_root}"
    else:
        # Logged-in first page — soft cap only.
        limit, window = (90, 60)
        bucket = f"feed:{ip}:{bucket_root}"

    try:
        rate_limit.check_rate_limit(bucket, limit=limit, window_sec=window)
    except ValueError:
        return rate_limited_response()

    # Anonymous first-page without browser/client signal → block.
    if not auth and not official and not has_browser_signal(request):
        return scrape_blocked_response()

    return None


def robots_txt_body() -> str:
    """Strict robots policy: refuse scrapers, AI trainers, and feed harvesting."""
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
Disallow: /trending
Disallow: /hashtags
Disallow: /communities
Disallow: /spaces
Disallow: /topics
Disallow: /feed
Disallow: /home
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
