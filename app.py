"""SMATSOULS attendance collection app."""

import logging

from flask import Flask, jsonify, redirect, render_template, request, url_for

import db
from validation import COUNTRIES, validate_submission

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_META = [
    {
        "key": "adults",
        "title": "Adults",
        "first_label": "Male",
        "second_label": "Female",
        "first_suffix": "m",
        "second_suffix": "f",
    },
    {
        "key": "youths",
        "title": "Youths",
        "first_label": "Male",
        "second_label": "Female",
        "first_suffix": "m",
        "second_suffix": "f",
    },
    {
        "key": "ypf",
        "title": "YPF",
        "first_label": "Male",
        "second_label": "Female",
        "first_suffix": "m",
        "second_suffix": "f",
    },
    {
        "key": "campus",
        "title": "Campus",
        "first_label": "Male",
        "second_label": "Female",
        "first_suffix": "m",
        "second_suffix": "f",
    },
    {
        "key": "children",
        "title": "Children",
        "first_label": "Boys",
        "second_label": "Girls",
        "first_suffix": "b",
        "second_suffix": "g",
    },
]


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
        return _render_form(
            values=request.form.to_dict(), errors=errors, status=400
        )

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
    return render_template("submissions.html", submissions=db.fetch_submissions())


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
