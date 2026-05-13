"""SQLite хранилище истории сканов.

Схема: одна таблица scans с полями для всего что нужно восстановить
после перезапуска сервера (пути, статус, images_dir, workspace).
"""
from __future__ import annotations

import sqlite3
import time
from contextlib import closing
from pathlib import Path

_DB_PATH: Path | None = None


# ── Инициализация ──────────────────────────────────────────────────────────────

def init_db(db_path: Path) -> None:
    """Установить путь к БД и создать таблицы если не существуют."""
    global _DB_PATH
    _DB_PATH = db_path
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


# ── Внутренний коннект ─────────────────────────────────────────────────────────

def _conn() -> closing:
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized — call init_db() first")
    c = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    c.row_factory = sqlite3.Row
    return closing(c)


# ── CRUD ───────────────────────────────────────────────────────────────────────

def insert_scan(*, name: str, images_dir: str, workspace: str = "") -> int:
    """Вставить запись о новом скане, вернуть id."""
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO scans (name, created_at, images_dir, workspace, status)
               VALUES (?, ?, ?, ?, 'running')""",
            (name, time.strftime("%Y-%m-%dT%H:%M:%S"), images_dir, workspace),
        )
        c.commit()
        return cur.lastrowid


def update_scan(scan_id: int, **kwargs) -> None:
    """Обновить произвольные поля записи по id."""
    if not kwargs:
        return
    cols = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [scan_id]
    with _conn() as c:
        c.execute(f"UPDATE scans SET {cols} WHERE id = ?", vals)
        c.commit()


def get_scan(scan_id: int) -> dict | None:
    """Получить одну запись по id, или None."""
    with _conn() as c:
        row = c.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    return dict(row) if row else None


def get_all_scans() -> list[dict]:
    """Все записи, новые первыми."""
    with _conn() as c:
        rows = c.execute("SELECT * FROM scans ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def get_last_done_scan() -> dict | None:
    """Последний скан со статусом done, или None."""
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM scans WHERE status = 'done' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def delete_scan(scan_id: int) -> None:
    """Удалить запись по id."""
    with _conn() as c:
        c.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        c.commit()
