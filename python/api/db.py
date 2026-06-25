"""SQLite хранилище истории сканов."""
from __future__ import annotations

import sqlite3
import time
from contextlib import closing
from pathlib import Path

_DB_PATH: Path | None = None


def init_db(db_path: Path) -> None:
    global _DB_PATH
    _DB_PATH = db_path
    # Пытаемся удалить залипшие файлы от предыдущей сессии (безопасно: uncommitted).
    for suffix in ("-journal", "-wal", "-shm"):
        try:
            Path(str(db_path) + suffix).unlink(missing_ok=True)
        except OSError:
            pass  # файл заблокирован — SQLite попробует восстановить сам
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                created_at  TEXT    NOT NULL,
                images_dir  TEXT    NOT NULL,
                workspace   TEXT    NOT NULL DEFAULT '',
                ply_path    TEXT,
                mesh_path   TEXT,
                status      TEXT    NOT NULL DEFAULT 'running',
                n_images    INTEGER,
                elapsed_sec REAL,
                error_msg   TEXT
            )
        """)


def _conn() -> closing:
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized — call init_db() first")
    c = sqlite3.connect(str(_DB_PATH), check_same_thread=False, timeout=10)
    c.row_factory = sqlite3.Row
    return closing(c)


def insert_scan(*, name: str, images_dir: str, workspace: str = "") -> int:
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO scans (name, created_at, images_dir, workspace, status)
               VALUES (?, ?, ?, ?, 'running')""",
            (name, time.strftime("%Y-%m-%dT%H:%M:%S"), images_dir, workspace),
        )
        c.commit()
        return cur.lastrowid


def update_scan(scan_id: int, **kwargs) -> None:
    if not kwargs:
        return
    cols = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [scan_id]
    with _conn() as c:
        c.execute(f"UPDATE scans SET {cols} WHERE id = ?", vals)
        c.commit()


def get_scan(scan_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    return dict(row) if row else None


def get_all_scans() -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM scans ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def get_last_done_scan() -> dict | None:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM scans WHERE status = 'done' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def delete_scan(scan_id: int) -> None:
    with _conn() as c:
        c.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        c.commit()
