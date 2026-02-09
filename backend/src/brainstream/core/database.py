"""SQLite state database for Thompson Sampling and action logs."""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from brainstream.core.config import settings

logger = logging.getLogger(__name__)

_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS cluster_arms (
    cluster_id INTEGER PRIMARY KEY,
    alpha REAL DEFAULT 1.0,
    beta REAL DEFAULT 1.0,
    article_count INTEGER DEFAULT 0,
    label TEXT DEFAULT '',
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS action_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL,
    action TEXT NOT NULL,
    cluster_id INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


def _get_db_path() -> Path:
    settings.ensure_data_dir()
    return settings.state_db_path


@contextmanager
def get_connection():
    """Get a SQLite connection with context manager."""
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the state database schema."""
    with get_connection() as conn:
        conn.executescript(_DB_SCHEMA)
    logger.info("State database initialized at %s", _get_db_path())


def get_cluster_arm(cluster_id: int) -> dict | None:
    """Get Thompson Sampling arm for a cluster."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM cluster_arms WHERE cluster_id = ?", (cluster_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_cluster_arms() -> list[dict]:
    """Get all Thompson Sampling arms."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM cluster_arms ORDER BY cluster_id").fetchall()
        return [dict(row) for row in rows]


def upsert_cluster_arm(
    cluster_id: int,
    alpha: float = 1.0,
    beta: float = 1.0,
    article_count: int = 0,
    label: str = "",
) -> None:
    """Insert or update a cluster arm."""
    now = datetime.now(UTC).isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO cluster_arms (cluster_id, alpha, beta, article_count, label, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(cluster_id) DO UPDATE SET
                alpha = excluded.alpha,
                beta = excluded.beta,
                article_count = excluded.article_count,
                label = CASE WHEN excluded.label != '' THEN excluded.label ELSE cluster_arms.label END,
                updated_at = excluded.updated_at""",
            (cluster_id, alpha, beta, article_count, label, now),
        )


def update_arm_reward(cluster_id: int, success: bool) -> None:
    """Update Thompson Sampling arm after user action."""
    now = datetime.now(UTC).isoformat()
    with get_connection() as conn:
        if success:
            conn.execute(
                "UPDATE cluster_arms SET alpha = alpha + 1, updated_at = ? WHERE cluster_id = ?",
                (now, cluster_id),
            )
        else:
            conn.execute(
                "UPDATE cluster_arms SET beta = beta + 1, updated_at = ? WHERE cluster_id = ?",
                (now, cluster_id),
            )


def log_action(article_id: str, action: str, cluster_id: int | None = None) -> None:
    """Log a user action."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO action_logs (article_id, action, cluster_id) VALUES (?, ?, ?)",
            (article_id, action, cluster_id),
        )


def get_action_logs(limit: int = 100) -> list[dict]:
    """Get recent action logs."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM action_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
