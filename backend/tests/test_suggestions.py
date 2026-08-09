"""Suggestions list unit checks (no network LLM)."""

from app.suggestions import CURATED, list_suggestions


class _FakeQuery:
    def filter(self, *a, **k):
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
