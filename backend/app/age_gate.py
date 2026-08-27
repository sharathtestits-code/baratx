"""Age / DOB eligibility (18+) for India DPDP children rules + US COPPA-safe floor."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

AGE_CONSENT_VERSION = "2026-08-27-age"
MIN_AGE_YEARS = 18


def parse_dob(value: Optional[str]) -> date:
    raw = (value or "").strip()
    try:
        y, m, d = (int(p) for p in raw.split("-"))
        dob = date(y, m, d)
    except Exception as exc:
        raise ValueError("Enter a valid date of birth (YYYY-MM-DD).") from exc
    if dob > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    return dob


def age_on(dob: date, on: Optional[date] = None) -> int:
    today = on or date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


def require_adult_dob(value: Optional[str]) -> date:
    dob = parse_dob(value)
    age = age_on(dob)
    if age > 120:
        raise ValueError("Enter a valid date of birth.")
    if age < MIN_AGE_YEARS:
        raise ValueError(
            f"BarathX is for people {MIN_AGE_YEARS}+. You cannot create an account if you are under {MIN_AGE_YEARS}."
        )
    return dob


def require_age_attestation(confirm_age_18: Optional[bool]) -> None:
    if not confirm_age_18:
        raise ValueError(
            f"Confirm you are {MIN_AGE_YEARS} or older and that your date of birth is accurate."
        )


def age_consent_stamp() -> tuple[datetime, str]:
    return datetime.now(timezone.utc), AGE_CONSENT_VERSION
