"""Suggestions list unit checks (no network LLM)."""

from app.suggestions import CURATED, CURATED_BY_TOPIC, list_suggestions


class _FakeQuery:
    def filter(self, *a, **k):
        return self

    def join(self, *a, **k):
        return self

    def outerjoin(self, *a, **k):
        return self

    def order_by(self, *a, **k):
        return self

    def limit(self, *a, **k):
        return self

    def all(self):
        return []


class _FakeDB:
    def query(self, *a, **k):
        return _FakeQuery()


def test_square_has_15_to_20():
    out = list_suggestions(_FakeDB(), surface="square", limit=20)
    assert out["ok"] is True
    assert 15 <= len(out["items"]) <= 20
    assert out["source"] == "curated+live"


def test_each_arena_bucket():
    for arena in ("sports", "politics", "entertainment", "news", "spirituality", "startups"):
        assert len(CURATED[arena]) >= 15
        out = list_suggestions(_FakeDB(), surface="arena", arena_key=arena, limit=20)
        assert len(out["items"]) >= 15


def test_badminton_topic_not_cricket_dominated():
    out = list_suggestions(
        _FakeDB(), surface="arena", arena_key="sports", topic_key="badminton", limit=20
    )
    assert out["ok"] is True
    assert out["topic_key"] == "badminton"
    assert out["source"] == "topic+live"
    texts = " ".join(i["text"].lower() for i in out["items"])
    assert "badminton" in texts
    # Must not be the generic cricket-heavy sports bucket.
    cricket_hits = sum(
        1
        for i in out["items"]
        if "cricket" in i["text"].lower()
        or "kohli" in i["text"].lower()
        or "ipl" in i["text"].lower()
    )
    assert cricket_hits <= 2
    assert any("badminton" in i["text"].lower() for i in out["items"][:5])


def test_topic_buckets_cover_major_sports():
    for key in ("badminton", "football-isl", "chess", "hockey", "ipl", "kabaddi"):
        assert key in CURATED_BY_TOPIC
        assert len(CURATED_BY_TOPIC[key]) >= 10
        out = list_suggestions(
            _FakeDB(), surface="arena", arena_key="sports", topic_key=key, limit=15
        )
        assert len(out["items"]) >= 10
        assert out["topic_key"] == key
