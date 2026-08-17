"""Tests for India-now trending lane resolution (no live RSS)."""

from app import trending


def test_resolve_cricket_lane():
    conf = trending.resolve_lane("cricket in india")
    assert conf["lane"] == "sports"
    assert conf["query_key"] == "cricket"


def test_resolve_news_over_trending():
    conf = trending.resolve_lane("what is trending in india on news")
    assert conf["lane"] == "news"
    assert conf["query_key"] == "news"


def test_resolve_politics():
    conf = trending.resolve_lane("Politics")
    assert conf["lane"] == "politics"


def test_topics_for_cricket_filter():
    conf = trending.resolve_lane("cricket")
    topics = trending._topics_for_lane(conf)
    keys = {t["key"] for t in topics}
    assert "ipl" in keys or "team-india" in keys
    assert "federalism" not in keys


def test_get_trending_taxonomy_fallback(monkeypatch):
    monkeypatch.setattr(trending, "_fetch_headlines", lambda conf, limit: [])
    trending._cache.clear()
    data = trending.get_trending(q="politics", limit=5)
    assert data["ok"] is True
    assert data["lane"] == "politics"
    assert len(data["topics"]) >= 1
    assert data["source"] == "taxonomy"
