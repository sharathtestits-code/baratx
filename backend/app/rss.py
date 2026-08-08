"""Unpaid RSS helpers — Google News IN search feeds → debate prompt titles."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import quote_plus, urlparse, parse_qs, unquote
from urllib.request import Request, urlopen

logger = logging.getLogger("baratx.rss")

USER_AGENT = "BharatXBot/1.0 (+https://barathx.com)"


def google_news_rss_url(query: str) -> str:
    q = quote_plus((query or "").strip())
    return f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"


def _clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", (title or "").strip())
    # Drop trailing " - Publisher"
    title = re.sub(r"\s+[-—|]\s+[^-—|]{2,40}$", "", title).strip()
    return title[:180]


def headline_to_debate_title(headline: str) -> str:
    """Turn a news headline into a fight people can join."""
    h = _clean_title(headline)
    if not h:
        return "Is this story being spun wrong?"
    if h.endswith("?"):
        return h
    # Light templates — keep short for mobile
    if len(h) > 90:
        h = h[:87].rsplit(" ", 1)[0] + "…"
    return f"Take: {h} — overblown or fair?"


def fetch_rss_items(query: str, limit: int = 5) -> list[dict]:
    """Fetch Google News RSS items. Returns [{title, link}]. Never raises to caller."""
    url = google_news_rss_url(query)
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=8) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        items = []
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not title:
                continue
            items.append({"title": _clean_title(title), "link": link})
            if len(items) >= limit:
                break
        return items
    except Exception:  # noqa: BLE001
        logger.exception("RSS fetch failed for query=%s", query)
        return []
