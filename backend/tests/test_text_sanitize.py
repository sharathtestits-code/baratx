"""Unit tests for bidi spoofing sanitization."""

from app.text_parse import sanitize_user_text


def test_strips_rtl_override_filename_spoof():
    # U+202E makes "gnp.exe" appear reversed as "exe.png" in many UIs
    spoofed = "download \u202egnp.exe\u202c now"
    cleaned = sanitize_user_text(spoofed)
    assert "\u202e" not in cleaned
    assert "\u202c" not in cleaned
    assert "gnp.exe" in cleaned
    assert cleaned == "download gnp.exe now"


def test_strips_isolate_controls():
    text = "hello\u2066world\u2069"
    assert sanitize_user_text(text) == "helloworld"


def test_keeps_normal_unicode():
    text = "नमस्ते 🇮🇳 from Hyderabad"
    assert sanitize_user_text(text) == text
