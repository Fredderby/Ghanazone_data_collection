# SMATSOULS Attendance Collection — Design Spec

Date: 2026-11-26

## Purpose
A single, mobile-friendly web form to collect one aggregated church attendance report per country (Sierra Leone, Ghana, Liberia) for Sunday, 29 November 2026, including online attendance. Submissions are stored in MySQL and can be reviewed on a simple read-only list page.

## Decisions (confirmed with user)
- One aggregate submission per country (not per-location rows).
- Each attendance category has its own in-person inputs (Male/Female; Boys/Girls for children); online attendance is captured in a single field for the whole report.
- Storage: MySQL Cloud Cluster using the credentials in `.env`.
- A simple read-only admin list of submissions is included.
- Standard project folders are allowed: `templates/` and `static/`.

## Stack
- Python 3.12, Flask, mysql-connector-python, python-dotenv.
- Frontend: plain HTML + CSS + vanilla JS (no build step, no npm).

## Files
- Root: `app.py` (Flask app, routes, DB access), `validation.py` (pure validation), `db.py` (MySQL access), `requirements.txt`, `.env`, `.env.example`, `DESIGN.md`, `PLAN.md`, `README.md`, `test_validation.py`, `test_app.py`.
- `templates/form.html` — collection form.
- `templates/submissions.html` — admin list.
- `static/styles.css` — all styling.
- `static/app.js` — live totals, validation, interactions.
- `.env` — normalized keys: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`. Values preserved; `.env.example` added.

## Data model
Table `submissions` (created automatically at startup if missing):

| Column | Type | Notes |
|---|---|---|
| id | INT AUTO_INCREMENT PK | |
| country | VARCHAR(50) | Sierra Leone / Ghana / Liberia |
| total_locations | INT | required, >= 0 |
| total_pastors | INT | required, >= 0 |
| workers_brothers | INT | required, >= 0 |
| workers_sisters | INT | required, >= 0 |
| total_online | INT | required, >= 0 — one online field for the whole report |
| adults_m, adults_f | INT | required, >= 0 |
| youths_m, youths_f | INT | required, >= 0 |
| ypf_m, ypf_f | INT | required, >= 0 |
| campus_m, campus_f | INT | required, >= 0 |
| children_b, children_g | INT | required, >= 0 |
| submitted_at | DATETIME | server timestamp |

Assumption: "church workers (brothers and sisters)" is two inputs (Brothers, Sisters) with an auto-computed total displayed in the UI. (User may change to one combined field.)

## Routes
- `GET /` — render `form.html`.
- `POST /submit` — validate all fields server-side, insert into MySQL, redirect to `/?submitted=1`.
- `GET /submissions` — render `submissions.html` with all rows ordered newest first.
- `GET /health` — simple `{"status":"ok"}` + DB check.

## Validation
- All fields required; country must be one of the three allowed values.
- Numeric fields must be non-negative integers (0 allowed).
- Errors returned to the form with inline messages and preserved values; no stack traces shown to users.

## UI / UX
- Gradient hero header with "Sunday, 29 November 2026" date badge.
- Sections: (1) Country & Summary, (2) Church Workers, (3) Attendance — five category cards (Adults, Youths, YPF, Campus, Children), each with Male / Female / Online inputs.
- Live summary strip: in-person total, online total, grand total; recalculates on input.
- Required markers, inline validation, focus/hover states, subtle animations, success banner with "Submit another" action.
- Mobile-first responsive layout, semantic labels, keyboard accessible.

## Error handling
- Missing DB config → clear startup message.
- DB connection/insert failure → friendly error on the form, details logged server-side.
- Unknown routes → 404 page.

## Verification
1. Install requirements into existing `env`.
2. Start Flask app; confirm `/`, `/submissions`, `/health` respond.
3. Submit a valid test record; confirm success banner and row in `/submissions` and in MySQL.
4. Submit invalid data (missing field, negative, non-integer, bad country); confirm rejected with inline errors and no DB row.
5. Check responsive layout and live totals in a browser.

## Out of scope
- Authentication, editing/deleting submissions, per-location entry, charts, deployment config, email notifications.
