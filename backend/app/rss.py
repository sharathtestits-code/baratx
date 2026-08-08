"""Unpaid RSS helpers — Google News IN search feeds with credible-source filtering."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

logger = logging.getLogger("baratx.rss")

USER_AGENT = "BaratXBot/1.0 (+https://barathx.com)"

# Publishers we trust for BaratX daily glimpses (matched against Google News " - Source").
CREDIBLE_SOURCES = (
    "the hindu",
    "indian express",
    "hindustan times",
    "times of india",
    "economic times",
    "livemint",
    "live mint",
    "business standard",
    "reuters",
    "associated press",
    "pti",
    "press trust of india",
    "ani",
    "asian news international",
    "pib",
    "press information bureau",
    "ndtv",
    "the print",
    "india today",
    "bbc",
    "bloomberg",
    "financial times",
    "moneycontrol",
    "the wire",
    "scroll.in",
    "scroll",
    "the quint",
    "deccan herald",
    "telegraph india",
    "outlook",
    "forbes india",
    "yourstory",
    "inc42",
    "entrackr",
    "techcrunch",
    "the ken",
)


def google_news_rss_url(query: str) -> str:
    q = quote_plus((query or "").strip())
    return f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"


def _split_title_source(raw_title: str) -> tuple[str, str]:
    """Google News titles are usually 'Headline - Publisher'."""
    raw = re.sub(r"\s+", " ", (raw_title or "").strip())
    parts = re.split(r"\s+[-—|]\s+", raw)
    if len(parts) >= 2:
        source = parts[-1].strip()
        headline = " - ".join(parts[:-1]).strip()
        return headline[:180], source[:80]
    return raw[:180], ""


def _clean_title(title: str) -> str:
    headline, _ = _split_title_source(title)
    return headline


def extract_source(title: str) -> str:
    _, source = _split_title_source(title)
    return source


def is_credible_source(source: str) -> bool:
    low = (source or "").strip().lower()
    if not low:
        return False
    return any(s in low for s in CREDIBLE_SOURCES)


def headline_to_debate_title(headline: str, *, arena_key: str | None = None) -> str:
    """Turn a news headline into a fight people can join.

    Avoids the repetitive "Take: … — overblown or fair?" bot pattern.
    Startups get Fund it / Pass framing.
    """
    h = _clean_title(headline)
    if not h:
        return "Is this story being spun wrong?"
    if h.endswith("?"):
        return h
    if len(h) > 90:
        h = h[:87].rsplit(" ", 1)[0] + "…"
    key = (arena_key or "").lower()
    if key == "startups":
        return f"Fund it or Pass: {h}"
    # Rotate templates by headline length so digests don't all rhyme.
    n = len(h) % 3
    if n == 0:
        return f"{h} — agree or push back?"
    if n == 1:
        return f"Is this fair? {h}"
    return f"Your take: {h}"


def fetch_rss_items(
    query: str,
    limit: int = 5,
    *,
    credible_only: bool = False,
) -> list[dict]:
    """Fetch Google News RSS items. Returns [{title, link, source, credible}].

    Never raises to caller. When credible_only=True, drops unknown publishers.
    """
    url = google_news_rss_url(query)
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=8) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
    except Exception:  # noqa: BLE001
        logger.exception("RSS fetch failed for query=%s", query)
        return []

    items = []
    for item in root.findall("./channel/item"):
        raw_title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not raw_title:
            continue
        title, source = _split_title_source(raw_title)
        # Prefer <source> tag when present
        source_el = item.find("source")
        if source_el is not None and (source_el.text or "").strip():
            source = (source_el.text or "").strip()[:80]
        credible = is_credible_source(source)
        if credible_only and not credible:
            continue
        if not title:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "source": source,
                "credible": credible,
            }
        )
        if len(items) >= limit:
            break
    return items
