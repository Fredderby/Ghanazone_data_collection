"""MySQL persistence for attendance submissions."""

import os

import mysql.connector
from dotenv import load_dotenv

from validation import ALL_FIELDS

load_dotenv()

_REQUIRED_CONFIG = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")


def _config():
    missing = [key for key in _REQUIRED_CONFIG if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Missing database configuration: " + ", ".join(missing) + ". Check .env."
        )
    return {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT") or 3306),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "connection_timeout": 10,
        "use_pure": True,
    }


def get_connection():
    return mysql.connector.connect(**_config())


def init_db():
    """Create the submissions table if it does not exist."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                country VARCHAR(50) NOT NULL,
                total_locations INT NOT NULL,
                total_pastors INT NOT NULL,
                workers_brothers INT NOT NULL,
                workers_sisters INT NOT NULL,
                total_online INT NOT NULL,
                adults_m INT NOT NULL,
                adults_f INT NOT NULL,
                youths_m INT NOT NULL,
                youths_f INT NOT NULL,
                ypf_m INT NOT NULL,
                ypf_f INT NOT NULL,
                campus_m INT NOT NULL,
                campus_f INT NOT NULL,
                children_b INT NOT NULL,
                children_g INT NOT NULL,
                submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        # Migrate tables created with per-category online columns.
        def has_column(name):
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'submissions' "
                "AND COLUMN_NAME = %s",
                (name,),
            )
            return cursor.fetchone()[0] > 0

        if has_column("adults_online"):
            if not has_column("total_online"):
                try:
                    cursor.execute("ALTER TABLE submissions ADD COLUMN total_online INT NOT NULL DEFAULT 0")
                except mysql.connector.errors.ProgrammingError as exc:
                    if exc.errno != 1060:
                        raise
                cursor.execute(
                    "UPDATE submissions SET total_online = "
                    "COALESCE(adults_online, 0) + COALESCE(youths_online, 0) + "
                    "COALESCE(ypf_online, 0) + COALESCE(campus_online, 0) + "
                    "COALESCE(children_online, 0)"
                )
            for legacy in ("adults_online", "youths_online", "ypf_online", "campus_online", "children_online"):
                cursor.execute(f"ALTER TABLE submissions MODIFY COLUMN {legacy} INT NULL DEFAULT 0")

        connection.commit()
        cursor.close()
    finally:
        connection.close()


def insert_submission(values):
    """Insert one validated submission and return its new id."""
    columns = ", ".join(ALL_FIELDS)
    placeholders = ", ".join(["%s"] * len(ALL_FIELDS))
    sql = f"INSERT INTO submissions ({columns}) VALUES ({placeholders})"

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, tuple(values[field] for field in ALL_FIELDS))
        new_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        return new_id
    finally:
        connection.close()


def fetch_submissions():
    """Return all submissions, newest first, as a list of dicts."""
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM submissions ORDER BY submitted_at DESC, id DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        connection.close()


def db_available():
    """Return True when the database is reachable, without raising."""
    try:
        connection = get_connection()
        connection.close()
        return True
    except Exception:
        return False
