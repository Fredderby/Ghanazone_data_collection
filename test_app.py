"""Tests for the Flask routes."""

import pytest

from app import app as flask_app
from test_validation import VALID_PAYLOAD


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def test_health_ok(client, monkeypatch):
    monkeypatch.setattr("app.db.db_available", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_form_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"29 November 2026" in response.data


def test_submit_valid_redirects(client, monkeypatch):
    captured = {}

    def fake_insert(values):
        captured.update(values)
        return 42

    monkeypatch.setattr("app.db.insert_submission", fake_insert)

    response = client.post("/submit", data=VALID_PAYLOAD)

    assert response.status_code == 302
    assert "/?submitted=1" in response.headers["Location"]
    assert captured["country"] == "Sierra Leone"
    assert captured["adults_m"] == 100
    assert captured["children_b"] == 50
    assert captured["total_online"] == 83


def test_submit_invalid_shows_errors(client, monkeypatch):
    payload = dict(VALID_PAYLOAD)
    del payload["total_pastors"]

    response = client.post("/submit", data=payload)

    assert response.status_code == 400
    assert b"This field is required." in response.data


def test_db_error_returns_friendly_message(client, monkeypatch):
    def boom(values):
        raise RuntimeError("connection refused")

    monkeypatch.setattr("app.db.insert_submission", boom)

    response = client.post("/submit", data=VALID_PAYLOAD)

    assert response.status_code == 500
    assert b"unable to save" in response.data.lower()
    assert b"connection refused" not in response.data.lower()


def test_empty_submissions_page(client, monkeypatch):
    monkeypatch.setattr("app.db.fetch_submissions", lambda: [])

    response = client.get("/submissions")

    assert response.status_code == 200
    assert b"No submissions yet" in response.data
