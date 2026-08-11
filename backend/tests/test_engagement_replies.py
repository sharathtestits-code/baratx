"""Unit tests for official engage copy (no DB)."""

from app.engagement_replies import (
    MAX_REPLY_LENGTH,
    _engage_baratx,
    _engage_sharath,
    _looks_like_slop,
    _welcome_baratx,
    _welcome_sharath,
    detect_topic,
)


def test_detect_topic_reels_genz_support():
    assert detect_topic("why gen z is so fast by doing reels") == "reels_speed"
    assert detect_topic("Gen Z attention span is cooked") == "genz"
    assert detect_topic("what should we fix in traffic today?") == "city"
    assert detect_topic("audio not coming") == "support"
    assert detect_topic("mic not working on unmute") == "support"
    assert detect_topic("hello") == "short"


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
        assert not _looks_like_slop(text)
        assert "almost deleted" not in text.lower()
        assert "uncomfortable detail" not in text.lower()


def test_engage_mentions_reels_context():
    texts = {_engage_baratx("sam", "why gen z is so fast by doing reels") for _ in range(20)}
    texts |= {_engage_sharath("sam", "why gen z is so fast by doing reels") for _ in range(20)}
    joined = " ".join(texts).lower()
    assert "reel" in joined or "speed" in joined or "attention" in joined or "scroll" in joined or "feed" in joined


def test_support_audio_asks_about_problem():
    texts = {_engage_baratx("sam", "audio not coming") for _ in range(15)}
    texts |= {_engage_sharath("sam", "audio not coming") for _ in range(15)}
    joined = " ".join(texts).lower()
    assert any(
        k in joined
        for k in ("mic", "unmute", "audio", "device", "permission", "hear", "phone", "desktop")
    )
    assert "uncomfortable detail" not in joined
    assert "almost deleted" not in joined


def test_slop_detector():
    assert _looks_like_slop('@x “audio not coming” — say more. What’s the part you almost deleted?')
    assert _looks_like_slop("@x don’t leave it at the headline. Give me the uncomfortable detail.")
    assert not _looks_like_slop("Hey @x — audio’s dead for you too? Mic permission on?")
