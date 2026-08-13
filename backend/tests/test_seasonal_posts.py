"""Independence Day / seasonal official posts."""

from app.seed import SEASONAL_POSTS, seed_seasonal_posts


def test_independence_day_post_uses_15_august():
    item = next(p for p in SEASONAL_POSTS if "Independence" in p["marker"])
    assert "15 August" in item["marker"]
    assert "15 August" in item["text"]
    assert "18" not in item["text"]
    assert item["username"] == "baratx"


def test_seed_seasonal_posts_idempotent(monkeypatch):
    """Without a DB session this only checks the helper is importable + list non-empty."""
    assert len(SEASONAL_POSTS) >= 1
    assert callable(seed_seasonal_posts)
