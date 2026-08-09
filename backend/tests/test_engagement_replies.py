"""Unit tests for official engage copy (no DB)."""

from app.engagement_replies import (
    MAX_REPLY_LENGTH,
    _engage_baratx,
    _engage_sharath,
    _welcome_baratx,
    _welcome_sharath,
    detect_topic,
)


def test_detect_topic_reels_genz():
    assert detect_topic("why gen z is so fast by doing reels") == "reels_speed"
    assert detect_topic("Gen Z attention span is cooked") == "genz"
    assert detect_topic("what should we fix in traffic today?") == "city"


def test_welcome_and_engage_under_limit_and_human():
    post = "why gen z is so fast by doing reels"
    for fn in (
        lambda: _welcome_baratx("akhilvydyula1111", post),
        lambda: _welcome_sharath("akhilvydyula1111", post),
        lambda: _engage_baratx("akhilvydyula1111", post),
        lambda: _engage_sharath("akhilvydyula1111", post),
    ):
        text = fn()
        assert text
        assert len(text) <= MAX_REPLY_LENGTH
        assert "@akhilvydyula1111" in text
        # Not the old twin bot lines only
        assert "Drop one real take from your city. I’ll read the replies." not in text


def test_engage_mentions_reels_context():
    texts = {_engage_baratx("sam", "why gen z is so fast by doing reels") for _ in range(20)}
    texts |= {_engage_sharath("sam", "why gen z is so fast by doing reels") for _ in range(20)}
    joined = " ".join(texts).lower()
    assert "reel" in joined or "speed" in joined or "attention" in joined or "scroll" in joined
