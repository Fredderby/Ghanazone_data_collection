"""Church attendance collection app with an admin backend."""

import hmac
import logging
import os
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import db
from validation import CATEGORY_FIELDS, COUNTRIES, validate_submission

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-secret-not-for-production")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_USER = os.getenv("ADMIN_USER", "dataanalyst")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "D@taAnalyst2026!")

CATEGORY_META = [
    {"key": "adults", "title": "Adults", "first_label": "Male", "second_label": "Female", "first_suffix": "m", "second_suffix": "f"},
    {"key": "youths", "title": "Youths", "first_label": "Male", "second_label": "Female", "first_suffix": "m", "second_suffix": "f"},
    {"key": "ypf", "title": "YPF", "first_label": "Male", "second_label": "Female", "first_suffix": "m", "second_suffix": "f"},
    {"key": "campus", "title": "Campus", "first_label": "Male", "second_label": "Female", "first_suffix": "m", "second_suffix": "f"},
    {"key": "children", "title": "Children", "first_label": "Boys", "second_label": "Girls", "first_suffix": "b", "second_suffix": "g"},
]


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def _row_online(row):
    return row["online_m"] + row["online_f"]


def _row_in_person(row):
    return sum(row[field] for field in CATEGORY_FIELDS)


def _row_grand(row):
    return _row_in_person(row) + _row_online(row)


def _country_summary(rows):
    summary = []
    for country in COUNTRIES:
        country_rows = [row for row in rows if row["country"] == country]
        summary.append(
            {
                "name": country,
                "count": len(country_rows),
                "grand": sum(_row_grand(row) for row in country_rows),
            }
        )
    return summary


def _defaulters(rows):
    submitted = {row["country"] for row in rows}
    return [country for country in COUNTRIES if country not in submitted]


def _render_form(values=None, errors=None, submitted=False, db_error=None, status=200):
    return (
        render_template(
            "form.html",
            values=values or {},
            errors=errors or {},
            submitted=submitted,
            db_error=db_error,
            countries=COUNTRIES,
            categories=CATEGORY_META,
        ),
        status,
    )


@app.route("/")
def form():
    return _render_form(submitted=request.args.get("submitted") == "1")


@app.route("/submit", methods=["POST"])
def submit():
    values, errors = validate_submission(request.form)
    if errors:
        return _render_form(values=request.form.to_dict(), errors=errors, status=400)

    try:
        db.insert_submission(values)
    except Exception:
        logger.exception("Failed to save attendance submission")
        return _render_form(
            values=request.form.to_dict(),
            db_error="We couldn't save your submission. Please try again.",
            status=500,
        )

    return redirect(url_for("form", submitted=1))


@app.route("/submissions")
def submissions():
    return redirect(url_for("admin_login"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if hmac.compare_digest(username, ADMIN_USER) and hmac.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["admin_authenticated"] = True
            next_url = request.args.get("next", "")
            if not next_url.startswith("/") or next_url.startswith("//"):
                next_url = url_for("admin_dashboard")
            return redirect(next_url)
        return (
            render_template("login.html", error="Invalid username or password", username=username),
            401,
        )
    return render_template("login.html", error=None, username="")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    rows = db.fetch_submissions()
    in_person = sum(_row_in_person(row) for row in rows)
    online = sum(_row_online(row) for row in rows)
    return render_template(
        "admin_dashboard.html",
        stats={
            "submissions": len(rows),
            "in_person": in_person,
            "online": online,
            "grand": in_person + online,
        },
        countries=_country_summary(rows),
        defaulters=_defaulters(rows),
        recent=rows[:5],
        grand=_row_grand,
    )


@app.route("/admin/defaulters")
@admin_required
def admin_defaulters():
    rows = db.fetch_submissions()
    return render_template(
        "admin_defaulters.html",
        defaulters=_defaulters(rows),
        countries=_country_summary(rows),
    )


@app.route("/admin/submissions")
@admin_required
def admin_submissions():
    return render_template(
        "submissions.html",
        submissions=db.fetch_submissions(),
        grand=_row_grand,
        online=_row_online,
    )


@app.route("/admin/submissions/<int:row_id>/delete", methods=["POST"])
@admin_required
def admin_delete_submission(row_id):
    if db.delete_submission(row_id):
        flash("Submission deleted.", "success")
    else:
        flash("Submission not found.", "error")
    return redirect(url_for("admin_submissions"))


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "database": "connected" if db.db_available() else "unavailable",
        }
    )


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
