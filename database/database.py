import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "evidenceguard.db"


def _connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the decisions table if it doesn't exist yet."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project_id TEXT NOT NULL,
                overall_status TEXT NOT NULL,
                decision TEXT NOT NULL,
                justification TEXT
            )
            """
        )


def save_decision(project_id, overall_status, decision, justification):
    """Save one reviewer decision."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO decisions
                (timestamp, project_id, overall_status, decision, justification)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                project_id,
                overall_status,
                decision,
                justification,
            ),
        )


def get_decisions():
    """Return all saved decisions, newest first, as a list of dictionaries."""
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT timestamp, project_id, overall_status, decision, justification
            FROM decisions
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]