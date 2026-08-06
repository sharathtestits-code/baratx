"""Unit tests for multi-arena daily digest selection (no network)."""

from collections import Counter

from app.daily_digest import (
    MAX_POSTS_PER_ARENA,
    MAX_POSTS_PER_DAY,
    MIN_SCORE_TO_POST,
    _score_headline,
    select_posts,
)


def test_score_prefers_civic_over_clickbait():
    civic = _score_headline(
        "Supreme Court hears election bond challenge in India", "politics"
    )
    junk = _score_headline("Horoscope tips to lose weight today", "entertainment")
    assert civic >= MIN_SCORE_TO_POST
    assert junk < MIN_SCORE_TO_POST


def test_select_caps_per_arena_and_day():
    titles = [
        ("Parliament passes civic bill in Delhi amid protest", "politics"),
        ("Another politics row over bill in Delhi parliament", "politics"),
        ("Third politics debate floods Lok Sabha today", "politics"),
        ("IPL final thriller in Mumbai keeps India awake", "sports"),
        ("ISRO launches new satellite from Sriharikota", "news"),
        ("Temple festival draws lakhs in Hyderabad", "spirituality"),
        ("Bollywood star tips to lose weight viral video", "entertainment"),
    ]
    cands = [
        {
            "title": t,
            "arena": a,
            "topic": a,
            "link": "",
            "score": _score_headline(t, a),
        }
        for t, a in titles
    ]
    picked = select_posts(sorted(cands, key=lambda x: -x["score"]))
    assert 1 <= len(picked) <= MAX_POSTS_PER_DAY
    assert max(Counter(p["arena"] for p in picked).values()) <= MAX_POSTS_PER_ARENA
    assert all(p["score"] >= MIN_SCORE_TO_POST for p in picked)
    assert not any("Horoscope" in p["title"] or "tips to" in p["title"].lower() for p in picked)
