"""Tests for the Flask routes."""

import pytest

from app import app as flask_app
from test_validation import VALID_PAYLOAD


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def login(client):
    with client.session_transaction() as session:
        session["admin_authenticated"] = True


def sample_row(country="Ghana", row_id=1):
    row = {key: int(value) for key, value in VALID_PAYLOAD.items() if key != "country"}
    row.update(country=country, id=row_id, submitted_at="2026-11-26 10:00:00")
    return row


def test_health_ok(client, monkeypatch):
    monkeypatch.setattr("app.db.db_available", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_form_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"29 November 2026" in response.data


def test_form_links_to_admin_panel(client):
    response = client.get("/")

    assert b'href="/admin"' in response.data


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
    assert captured["online_m"] == 40
    assert captured["online_f"] == 43


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


def test_public_submissions_redirects_to_admin_login(client):
    response = client.get("/submissions")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


@pytest.mark.parametrize("path", ["/admin", "/admin/defaulters", "/admin/submissions"])
def test_admin_pages_require_login(client, path):
    response = client.get(path)

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_login_page_loads(client):
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert b"Admin sign in" in response.data


def test_login_with_valid_credentials(client, monkeypatch):
    monkeypatch.setattr("app.ADMIN_USER", "dataanalyst")
    monkeypatch.setattr("app.ADMIN_PASSWORD", "secret123")

    response = client.post(
        "/admin/login",
        data={"username": "dataanalyst", "password": "secret123"},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/admin"


def test_login_with_invalid_credentials(client, monkeypatch):
    monkeypatch.setattr("app.ADMIN_USER", "dataanalyst")
    monkeypatch.setattr("app.ADMIN_PASSWORD", "secret123")

    response = client.post(
        "/admin/login",
        data={"username": "dataanalyst", "password": "wrong"},
    )

    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_dashboard_shows_totals(client, monkeypatch):
    monkeypatch.setattr("app.db.fetch_submissions", lambda: [sample_row()])
    login(client)

    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"693" in response.data


def test_defaulters_lists_countries_without_submissions(client, monkeypatch):
    monkeypatch.setattr("app.db.fetch_submissions", lambda: [sample_row("Ghana")])
    login(client)

    response = client.get("/admin/defaulters")

    assert response.status_code == 200
    assert b"Sierra Leone" in response.data
    assert b"Liberia" in response.data
    assert b"Ghana" not in response.data


def test_delete_requires_login(client, monkeypatch):
    def boom(row_id):
        raise AssertionError("delete must not run for anonymous users")

    monkeypatch.setattr("app.db.delete_submission", boom)

    response = client.post("/admin/submissions/1/delete")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_delete_removes_submission(client, monkeypatch):
    deleted = []
    monkeypatch.setattr("app.db.delete_submission", lambda row_id: deleted.append(row_id) or True)
    login(client)

    response = client.post("/admin/submissions/7/delete")

    assert response.status_code == 302
    assert deleted == [7]


def test_admin_submission_report_shows_delete_control(client, monkeypatch):
    monkeypatch.setattr("app.db.fetch_submissions", lambda: [sample_row()])
    login(client)

    response = client.get("/admin/submissions")

    assert response.status_code == 200
    assert b"Delete" in response.data
    assert b"/admin/submissions/1/delete" in response.data


def test_delete_submission_removes_matching_row(monkeypatch):
    import db

    class FakeCursor:
        rowcount = 1

        def execute(self, sql, params):
            self.params = params

        def close(self):
            pass

    class FakeConnection:
        def cursor(self):
            return cursor

        def commit(self):
            pass

        def close(self):
            pass

    cursor = FakeCursor()
    monkeypatch.setattr("db.get_connection", lambda: FakeConnection())

    assert db.delete_submission(5) is True
    assert cursor.params == (5,)


def test_delete_submission_returns_false_when_no_row_matched(monkeypatch):
    import db

    class FakeCursor:
        rowcount = 0

        def execute(self, sql, params):
            pass

        def close(self):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr("db.get_connection", lambda: FakeConnection())

    assert db.delete_submission(99) is False
