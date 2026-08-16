"""Tests for heuristic AI-slop filter and anti-scrape helpers."""

from app import ai_filter, anti_scrape


def test_human_short_take_passes():
    score = ai_filter.score_ai_text("Hyderabad traffic is a joke. Fix footpaths first.")
    assert not score.reject
    assert not score.likely_ai


def test_self_id_rejects():
    score = ai_filter.score_ai_text("As an AI language model, I think both sides have merit.")
    assert score.reject
    assert score.likely_ai


def test_chatgpt_essay_flags_or_rejects():
    text = (
        "Certainly! It's important to note that furthermore, in today's world, "
        "we must delve into the landscape of policy. On one hand growth, "
        "on the other hand equity. In conclusion, a nuanced perspective is key."
    )
    score = ai_filter.score_ai_text(text)
    assert score.likely_ai
    assert score.reject


def test_emdash_formal_flags():
    text = (
        "It is important to note that the situation is multifaceted — "
        "furthermore, we must consider several factors carefully."
    )
    score = ai_filter.score_ai_text(text)
    assert score.likely_ai


def test_scraper_ua_blocked():
    assert anti_scrape.is_scraper_ua("python-requests/2.31.0")
    assert anti_scrape.is_scraper_ua("Scrapy/2.11.0 (+https://scrapy.org)")
    assert anti_scrape.is_scraper_ua("")
    assert anti_scrape.is_scraper_ua("GPTBot/1.0")


def test_browser_ua_allowed():
    assert not anti_scrape.is_scraper_ua(
        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
    )
    assert not anti_scrape.is_scraper_ua("Twitterbot/1.0")
    assert not anti_scrape.is_scraper_ua("facebookexternalhit/1.1")


def test_bulk_paths():
    assert anti_scrape.is_bulk_scrape_path("/posts")
    assert anti_scrape.is_bulk_scrape_path("/posts/abc/replies")
    assert not anti_scrape.is_bulk_scrape_path("/health")
    assert not anti_scrape.is_bulk_scrape_path("/auth/google")
