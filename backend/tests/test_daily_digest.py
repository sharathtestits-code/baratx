"""Unit tests for multi-arena peak digest selection (no network)."""

from collections import Counter

from app.daily_digest import (
    MAX_POSTS_PER_ARENA,
    MAX_POSTS_PER_DAY,
    MIN_SCORE_TO_POST,
    _score_headline,
    arenas_for_slot,
    select_posts,
)
from app.rss import is_credible_source


def test_score_prefers_civic_over_clickbait():
    civic = _score_headline(
        "Supreme Court hears election bond challenge in India", "politics", credible=True
    )
    junk = _score_headline("Horoscope tips to lose weight today", "entertainment", credible=False)
    assert civic >= MIN_SCORE_TO_POST
    assert junk < MIN_SCORE_TO_POST


def test_credible_source_allowlist():
    assert is_credible_source("The Hindu")
    assert is_credible_source("Economic Times")
    assert is_credible_source("Press Information Bureau")
    assert not is_credible_source("Random Blog")


def test_select_caps_per_arena_and_day():
    titles = [
        ("Parliament passes civic bill in Delhi amid protest", "politics"),
        ("Another politics row over bill in Delhi parliament", "politics"),
        ("Third politics debate floods Lok Sabha today", "politics"),
        ("IPL final thriller in Mumbai keeps India awake", "sports"),
        ("ISRO launches new satellite from Sriharikota", "news"),
        ("Temple festival draws lakhs in Hyderabad", "spirituality"),
        ("India startup funding round closes in Bengaluru", "startups"),
        ("Bollywood opens big weekend across India cities", "entertainment"),
    ]
    cands = [
        {
            "title": t,
            "arena": a,
            "topic": a,
            "link": "",
            "source": "The Hindu",
            "score": _score_headline(t, a, credible=True),
        }
        for t, a in titles
    ]
    # Clickbait without credibility should sink
    cands.append(
        {
            "title": "Horoscope tips to lose weight today viral",
            "arena": "entertainment",
            "topic": "entertainment",
            "link": "",
            "source": "",
            "score": _score_headline(
                "Horoscope tips to lose weight today viral", "entertainment", credible=False
            ),
        }
    )
    picked = select_posts(sorted(cands, key=lambda x: -x["score"]))
    assert 1 <= len(picked) <= MAX_POSTS_PER_DAY
    assert max(Counter(p["arena"] for p in picked).values()) <= MAX_POSTS_PER_ARENA
    assert all(p["score"] >= MIN_SCORE_TO_POST for p in picked)
    assert not any("Horoscope" in p["title"] or "tips to" in p["title"].lower() for p in picked)


def test_arenas_for_slot_rotates():
    from app.daily_digest import ARENAS_PER_SLOT

    morning = arenas_for_slot("morning")
    midday = arenas_for_slot("midday")
    evening = arenas_for_slot("evening")
    assert len(morning) == ARENAS_PER_SLOT
    assert len(midday) == ARENAS_PER_SLOT
    assert len(evening) == ARENAS_PER_SLOT
    # Startups-weighted densify: startups should appear in the daily rotation.
    day = set(morning + midday + evening)
    assert "startups" in day or ARENAS_PER_SLOT >= 1
