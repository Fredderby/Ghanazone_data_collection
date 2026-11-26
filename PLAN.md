# Deeper Life Bible Church — Attendance Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a simple, polished Flask web app that collects one aggregated country attendance report and stores it in MySQL.

**Architecture:** Standard Flask app in the project root with `templates/` and `static/` folders. `validation.py` owns pure validation; `db.py` owns MySQL access; `app.py` wires routes. Frontend is plain HTML/CSS/JS with no build step.

**Tech Stack:** Python 3.12, Flask, mysql-connector-python, python-dotenv, pytest.

**Spec:** `DESIGN.md`

## Global Constraints
- Work in `F:\DEVELOPED APPS\SMATSOULS`; standard `templates/` and `static/` folders are allowed.
- Countries exactly: Sierra Leone, Ghana, Liberia.
- Report date exactly: Sunday, 29 November 2026.
- Attendance categories exactly: adults, youths, ypf, campus, children, with only in-person inputs (`m`/`f`, children `b`/`g`); online attendance is one `total_online` field.
- Every field is required; numeric values must be non-negative integers (0 allowed).
- DB config keys: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
- No authentication, no build tooling, no npm.

## Review Focus
- Missing/blank required field → rejected with inline error, no DB row. Test: `test_missing_required_field`.
- Negative or non-integer numeric value → rejected, no DB row. Test: `test_negative_value`, `test_non_integer_value`.
- Country outside the three allowed values → rejected. Test: `test_invalid_country`.
- DB unreachable/misconfigured → friendly error, no stack trace to user. Test: `test_db_error_returns_friendly_message`.
- Duplicate/empty submission list rendering → admin page shows empty state, not an error. Test: `test_empty_submissions_page`.

---

### Task 1: Config & dependencies

**Files:**
- Create: `requirements.txt`, `.env.example`
- Modify: `.env` (normalize keys, preserve values)

**Interfaces:**
- Produces: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` loadable via python-dotenv.

- [ ] **Step 1: Write requirements.txt**

`Flask`, `mysql-connector-python`, `python-dotenv`, `pytest`, `gunicorn`.

- [ ] **Step 2: Normalize `.env` and create `.env.example`**

Map line 1→`DB_HOST=mysql-202931-0.cloudclusters.net`, line 2→`DB_PORT=19944`, line 4→`DB_USER`, line 5→`DB_PASSWORD`, line 6→`DB_NAME=smatsouls`. Preserve values verbatim. `.env.example` contains keys with blank/example values.

- [ ] **Step 3: Install dependencies**

Run: `env\Scripts\pip install -r requirements.txt`
Expected: all packages install into the existing venv.

### Task 2: Validation

**Files:**
- Create: `validation.py`, `test_validation.py`

**Interfaces:**
- Produces: `validate_submission(data: dict) -> tuple[dict, dict]` returning `(clean_values, errors)`. `clean_values` maps field name → int (country stays str). `errors` maps field name → message.

- [ ] **Step 1: Write failing tests**

Tests: valid payload → no errors and ints; `test_missing_required_field`; `test_negative_value`; `test_non_integer_value`; `test_invalid_country`; `test_zero_allowed`.

- [ ] **Step 2: Run tests, verify FAIL**

Run: `env\Scripts\pytest test_validation.py -v`

- [ ] **Step 3: Implement `validate_submission`**

Fields: `country`, `total_locations`, `total_pastors`, `workers_brothers`, `workers_sisters`, one `total_online` field, then 10 category in-person fields: `{cat}_m`, `{cat}_f` for adults/youths/ypf/campus and `children_b`, `children_g`. Required, non-negative integer parsing, country allowlist.

- [ ] **Step 4: Run tests, verify PASS**

- [ ] **Step 5: Commit** (skip — not a git repo; note in status)

### Task 3: Database layer

**Files:**
- Create: `db.py`

**Interfaces:**
- Consumes: env DB keys.
- Produces: `init_db() -> None`, `insert_submission(values: dict) -> int`, `fetch_submissions() -> list[dict]`, `db_available() -> bool`.

- [ ] **Step 1: Implement `init_db`**

`CREATE TABLE IF NOT EXISTS submissions` with columns from `DESIGN.md`, `id` AUTO_INCREMENT PK, `submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP`. Use mysql-connector with `connection_timeout` and `use_pure=True`.

- [ ] **Step 2: Implement `insert_submission(values)`**

Parameterized insert of all 16 data columns; return new row id; close connection in `finally`.

- [ ] **Step 3: Implement `fetch_submissions()` and `db_available()`**

Select all ordered by `submitted_at DESC, id DESC`, return list of dicts. `db_available()` returns bool without raising.

- [ ] **Step 4: Verify against live MySQL**

Run a short Python snippet: `init_db()`, `db_available()`, `fetch_submissions()` — expect no exceptions and a table created.

### Task 4: Routes & app wiring

**Files:**
- Create: `app.py`, `test_app.py`

**Interfaces:**
- Consumes: `validate_submission`, `db` functions.
- Produces: Flask `app`, routes `/`, `/submit`, `/submissions`, `/health`.

- [ ] **Step 1: Write failing tests**

`test_health_ok`, `test_form_page_loads`, `test_submit_valid_redirects`, `test_submit_invalid_shows_errors`, `test_db_error_returns_friendly_message`, `test_empty_submissions_page` (uses a temporary in-memory stub for db functions).

- [ ] **Step 2: Run tests, verify FAIL**

- [ ] **Step 3: Implement `app.py`**

Load `.env`; configure `template_folder='.'`, `static_folder='.'`, `static_url_path='/static'`. Routes: `GET /` render `form.html`; `POST /submit` validate → on error re-render form with errors + preserved values and status 400; on success insert then redirect `/?submitted=1`; `GET /submissions` render list; `GET /health` JSON status + db flag. Catch DB exceptions and render form with `db_error`.

- [ ] **Step 4: Run tests, verify PASS**

### Task 5: Frontend (form, styles, JS, admin list)

**Files:**
- Create: `templates/form.html`, `templates/submissions.html`, `static/styles.css`, `static/app.js`

- [ ] **Step 1: Build `templates/form.html`**

Jinja template. Gradient hero with date badge; sections for Country & Summary, Church Workers; five category cards with labelled Male/Female/Online inputs (children: Boys/Girls/Online); live summary strip; inline error spans; success banner when `submitted=1`; link to `/submissions`; required markers; submit button. All inputs `required`, `type=number`, `min=0`, `inputmode=numeric`, names matching validation fields, values preserved from `values` dict.

- [ ] **Step 2: Build `static/styles.css`**

Modern, polished, mobile-first: gradient hero, card shadows, rounded corners, focus rings, error styling, responsive grid, animated success banner, accessible contrast, no external assets.

- [ ] **Step 3: Build `static/app.js`**

Recalculate in-person / online / grand totals on input; clamp negatives; highlight invalid fields; simple submit loading state.

- [ ] **Step 4: Build `templates/submissions.html`**

Read-only table of submissions with totals; empty state; link back to form. No external assets.

- [ ] **Step 5: Visual/manual check**

Run app, open `/`, confirm layout, live totals, validation states, and `/submissions` empty state.

### Task 6: Documentation & end-to-end verification

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

Setup (`pip install -r requirements.txt`), run (`python app.py`), URLs, DB table note.

- [ ] **Step 2: Run full test suite**

Run: `env\Scripts\pytest -v`
Expected: all tests pass.

- [ ] **Step 3: Live smoke test**

Start app; submit a valid record via HTTP; confirm success, row in `/submissions`, and row in MySQL; confirm invalid submission is rejected.
