"""Rotating BarathX product features for daily social packs.

One primary feature per IST day (deterministic), so creatives + copy stay fresh.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Feature:
    key: str
    name: str
    one_liner: str
    bullets: tuple[str, ...]
    screen: str  # key into render screen map
    template: str  # layout family for stills
    hashtags: str
    founding_ok: bool = False


# Order = rotation. Day-of-year % len picks the feature.
FEATURES: tuple[Feature, ...] = (
    Feature(
        key="square",
        name="Square",
        one_liner="Takes that stay on the record — not buried comments.",
        bullets=("Short posts that stay", "Real replies, not vanish", "India talking, out loud"),
        screen="square",
        template="phone_right",
        hashtags="#BarathX #Square #India #PublicSquare",
    ),
    Feature(
        key="arenas",
        name="Arenas",
        one_liner="Pick a side. Agree or Disagree. Real stakes.",
        bullets=("Forced sides", "For vs Against", "Debate with receipts"),
        screen="arenas",
        template="split_cards",
        hashtags="#BarathX #Arenas #Debate #India",
    ),
    Feature(
        key="live",
        name="Live",
        one_liner="Argue it live — human voices, sided rooms.",
        bullets=("Live rooms", "Talk on the record", "No scroll theater"),
        screen="live",
        template="phone_center",
        hashtags="#BarathX #Live #India #ArgueLive",
    ),
    Feature(
        key="explore",
        name="Explore",
        one_liner="Find people or topics — clear, not buried.",
        bullets=("@username → people", "Topic → India now", "No noisy dump"),
        screen="explore",
        template="search_focus",
        hashtags="#BarathX #Explore #India #Discover",
    ),
    Feature(
        key="human_first",
        name="Human-first",
        one_liner="AI drafts get demoted. Real takes rise.",
        bullets=("No AI slop", "Human ranking first", "Flagged drafts sink"),
        screen="home",
        template="bold_type",
        hashtags="#BarathX #HumanFirst #NoAISlop #India",
    ),
    Feature(
        key="founding",
        name="Founding 100",
        one_liner="100 Founding spots, earned by opening a debate that gets real engagement, not by signing up.",
        bullets=("Earned, not bought", "Open a real debate", "Early voices get seen"),
        screen="rewards",
        template="founding_banner",
        hashtags="#BarathX #Founding #BuildInPublic #India",
        founding_ok=True,
    ),
    Feature(
        key="soft_launch",
        name="Soft launch",
        one_liner="Android soft launch open — install APK, join with phone OTP.",
        bullets=("barathx.com/get-app", "Continue with phone", "No Play wait"),
        screen="login_phone",
        template="launch_hero",
        hashtags="#BarathX #SoftLaunch #India #PublicSquare",
    ),
)


def feature_for_date(d: date) -> Feature:
    idx = d.toordinal() % len(FEATURES)
    return FEATURES[idx]


def feature_by_key(key: str) -> Feature | None:
    k = (key or "").strip().lower()
    for f in FEATURES:
        if f.key == k:
            return f
    return None
