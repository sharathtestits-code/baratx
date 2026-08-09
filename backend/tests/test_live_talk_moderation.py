"""Live Talk join cap + auto-mod smoke tests."""

from datetime import datetime, timezone

from app import models, moderation as mod


def test_live_talk_max_constant():
    assert mod.LIVE_TALK_MAX == 15


def test_severe_text_detected():
    assert mod.text_violation_level("please kys now") == "severe"
    assert mod.text_violation_level("hello friends") is None


def test_guideline_reason():
    assert mod.reason_is_guideline("misleading spam")
    assert mod.reason_is_guideline("nice shoes") is False


def test_talk_participant_model_fields():
    row = models.LiveTalkParticipant(
        space_id="s1",
        user_id="u1",
        muted=True,
        video_enabled=False,
        joined_at=datetime.now(timezone.utc),
    )
    assert row.muted is True
    assert row.video_enabled is False
