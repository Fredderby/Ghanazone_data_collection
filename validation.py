"""Pure validation for attendance submissions."""

import re

COUNTRIES = ("Sierra Leone", "Ghana", "Liberia")

SUMMARY_FIELDS = (
    "total_locations",
    "total_pastors",
    "workers_brothers",
    "workers_sisters",
)

ONLINE_FIELD = "total_online"

CATEGORY_SUFFIXES = {
    "adults": ("m", "f"),
    "youths": ("m", "f"),
    "ypf": ("m", "f"),
    "campus": ("m", "f"),
    "children": ("b", "g"),
}
CATEGORY_FIELDS = tuple(
    f"{category}_{suffix}"
    for category, suffixes in CATEGORY_SUFFIXES.items()
    for suffix in suffixes
)

NUMERIC_FIELDS = SUMMARY_FIELDS + (ONLINE_FIELD,) + CATEGORY_FIELDS
ALL_FIELDS = ("country",) + NUMERIC_FIELDS


def validate_submission(data):
    """Return (clean_values, errors) for a raw submission dict."""
    clean = {}
    errors = {}

    country = str(data.get("country") or "").strip()
    if country in COUNTRIES:
        clean["country"] = country
    else:
        errors["country"] = "Please select a valid country."

    for name in NUMERIC_FIELDS:
        raw = data.get(name)
        text = "" if raw is None else str(raw).strip()
        if not text:
            errors[name] = "This field is required."
        elif not re.fullmatch(r"\d+", text):
            errors[name] = "Enter a whole number of 0 or more."
        else:
            clean[name] = int(text)

    return clean, errors
