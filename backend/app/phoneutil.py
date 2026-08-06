"""Normalize and validate phone numbers for OTP signup/login."""

from __future__ import annotations

import re

E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_phone(raw: str, default_region: str | None = None) -> str:
    """
    Normalize user input to E.164 (+XXXXXXXX).

    Accepts spaces, dashes, parentheses. Uses default_region when the user
    enters a national number without a country code:
      - "IN" → +91 for 10-digit mobiles (starting 6–9)
      - "US" → +1 for 10-digit numbers
    """
    s = (raw or "").strip()
    if not s:
        raise ValueError("Enter a phone number with country code, e.g. +919876543210")

    has_plus = s.startswith("+")
    digits = re.sub(r"\D", "", s)
    if not digits:
        raise ValueError("Enter a valid phone number with country code, e.g. +919876543210")

    region = (default_region or "").upper().strip() or None

    # India trunk prefix: 0XXXXXXXXXX
    if len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
        digits = "91" + digits[1:]
        has_plus = True

    if not has_plus:
        if len(digits) == 10:
            if region == "US":
                digits = "1" + digits
            elif region == "IN":
                if digits[0] not in "6789":
                    raise ValueError("Enter a valid 10-digit Indian mobile number")
                digits = "91" + digits
            elif digits[0] in "6789":
                # India-first default when no country selected
                digits = "91" + digits
            else:
                raise ValueError("Include country code, e.g. +91… or +1…")
        elif len(digits) == 11 and digits.startswith("1"):
            pass  # US/CA without +
        elif len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
            pass  # India without +
        else:
            raise ValueError("Include country code, e.g. +919876543210 or +12025550123")

    if len(digits) < 8 or len(digits) > 15:
        raise ValueError("Enter a valid phone number with country code, e.g. +919876543210 or +12025550123")

    if digits.startswith("0"):
        raise ValueError("Enter a valid phone number with country code, e.g. +919876543210")

    e164 = "+" + digits
    if not E164_RE.match(e164):
        raise ValueError("Enter a valid phone number with country code, e.g. +919876543210 or +12025550123")

    if e164.startswith("+91") and len(digits) != 12:
        raise ValueError("Indian numbers should be +91 followed by 10 digits")
    if e164.startswith("+1") and len(digits) != 11:
        raise ValueError("US/Canada numbers should be +1 followed by 10 digits")

    return e164
