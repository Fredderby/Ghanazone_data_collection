"""Tests for attendance submission validation."""

import pytest

from validation import validate_submission


VALID_PAYLOAD = {
    "country": "Sierra Leone",
    "total_locations": "12",
    "total_pastors": "8",
    "workers_brothers": "20",
    "workers_sisters": "35",
    "total_online": "83",
    "adults_m": "100",
    "adults_f": "150",
    "youths_m": "30",
    "youths_f": "45",
    "ypf_m": "15",
    "ypf_f": "25",
    "campus_m": "60",
    "campus_f": "80",
    "children_b": "50",
    "children_g": "55",
}


def test_valid_payload_returns_clean_integers_and_no_errors():
    clean, errors = validate_submission(dict(VALID_PAYLOAD))

    assert errors == {}
    assert clean["country"] == "Sierra Leone"
    assert clean["total_locations"] == 12
    assert clean["total_online"] == 83
    assert clean["children_b"] == 50
    assert isinstance(clean["workers_sisters"], int)


def test_missing_required_field_is_rejected():
    payload = dict(VALID_PAYLOAD)
    del payload["total_pastors"]

    clean, errors = validate_submission(payload)

    assert "total_pastors" in errors
    assert errors["total_pastors"]


def test_blank_required_field_is_rejected():
    payload = dict(VALID_PAYLOAD)
    payload["adults_m"] = "   "

    clean, errors = validate_submission(payload)

    assert "adults_m" in errors


def test_negative_value_is_rejected():
    payload = dict(VALID_PAYLOAD)
    payload["total_locations"] = "-1"

    clean, errors = validate_submission(payload)

    assert "total_locations" in errors


def test_non_integer_value_is_rejected():
    payload = dict(VALID_PAYLOAD)
    payload["adults_m"] = "3.5"

    clean, errors = validate_submission(payload)

    assert "adults_m" in errors


def test_invalid_country_is_rejected():
    payload = dict(VALID_PAYLOAD)
    payload["country"] = "Nigeria"

    clean, errors = validate_submission(payload)

    assert "country" in errors


def test_zero_is_accepted():
    payload = {key: ("0" if key != "country" else "Ghana") for key in VALID_PAYLOAD}

    clean, errors = validate_submission(payload)

    assert errors == {}
    assert clean["adults_m"] == 0
    assert clean["total_online"] == 0
