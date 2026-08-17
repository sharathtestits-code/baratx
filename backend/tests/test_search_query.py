"""Unit tests for Explore search query normalization."""

from app import search_query


def test_normalize_strips_handles():
    assert search_query.normalize_search_query("  #Politics ") == "Politics"
    assert search_query.normalize_search_query("@baratx") == "baratx"
    assert search_query.normalize_search_query("   ") == ""


def test_escape_like_wildcards():
    assert search_query.escape_like("100%") == r"100\%"
    assert search_query.escape_like("a_b") == r"a\_b"
    assert search_query.like_pattern("a%b") == r"%a\%b%"


def test_startup_india_variants():
    variants = search_query.search_variants("StartupIndia")
    folded = {v.casefold() for v in variants}
    assert "startupindia" in folded
    assert "startup india" in folded
    assert "startup" in folded
    assert "india" in folded


def test_geopolitics_variants():
    variants = search_query.search_variants("Geopolitics")
    assert any(v.casefold() == "geopolitics" for v in variants)
