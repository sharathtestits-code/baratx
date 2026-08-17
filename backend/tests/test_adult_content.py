"""Adult / sexual content block for public square text."""

import pytest

from app.moderation import (
    ADULT_BLOCK_MESSAGE,
    assert_safe_public_text,
    is_adult_or_sexual_content,
    text_violation_level,
)
from app.schemas import MessageCreate, ReplyCreate


def test_blocks_explicit_adult_phrases():
    assert is_adult_or_sexual_content("check this porn link")
    assert is_adult_or_sexual_content("send nudes")
    assert is_adult_or_sexual_content("OnlyFans promo")


def test_allows_normal_debate():
    assert not is_adult_or_sexual_content("Hyderabad traffic is broken. Fix footpaths.")
    assert not is_adult_or_sexual_content("Parliament should debate the bill today.")


def test_assert_raises_clear_message():
    with pytest.raises(ValueError, match="Adult or sexual content"):
        assert_safe_public_text("nsfw pics tonight")
    assert ADULT_BLOCK_MESSAGE


def test_message_schema_rejects_adult():
    with pytest.raises(Exception):
        MessageCreate(text="buy onlyfans here")


def test_reply_schema_allows_clean():
    msg = ReplyCreate(text="Agree — evidence please.")
    assert "Agree" in msg.text


def test_adult_is_severe_for_talk_moderation():
    assert text_violation_level("free porn hub") == "severe"
