"""Тесты api/db.py — CRUD операции с SQLite (не требуют сервера)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import api.db as db


# ── Фикстура: свежая БД на каждый тест ────────────────────────────────────────

@pytest.fixture()
def fresh(tmp_path):
    db.init_db(tmp_path / "scans.db")
    yield
    db._DB_PATH = None  # сбросить после теста


# ── init ───────────────────────────────────────────────────────────────────────

def test_init_creates_file(tmp_path):
    p = tmp_path / "test.db"
    db.init_db(p)
    assert p.exists()


def test_init_idempotent(tmp_path):
    p = tmp_path / "test.db"
    db.init_db(p)
    db.init_db(p)  # второй вызов не должен падать


# ── insert_scan ────────────────────────────────────────────────────────────────

def test_insert_returns_positive_id(fresh):
    sid = db.insert_scan(name="t1", images_dir="D:/p", workspace="D:/ws")
    assert isinstance(sid, int) and sid > 0


def test_insert_default_status_running(fresh):
    sid = db.insert_scan(name="t2", images_dir="x", workspace="y")
    assert db.get_scan(sid)["status"] == "running"


def test_insert_ply_is_null(fresh):
    sid = db.insert_scan(name="t3", images_dir="x", workspace="y")
    assert db.get_scan(sid)["ply_path"] is None


# ── get_scan ───────────────────────────────────────────────────────────────────

def test_get_scan_fields(fresh):
    sid = db.insert_scan(name="fields", images_dir="D:/photos", workspace="D:/ws")
    s   = db.get_scan(sid)
    assert s["name"] == "fields"
    assert s["images_dir"] == "D:/photos"
    assert s["workspace"] == "D:/ws"


def test_get_scan_nonexistent(fresh):
    assert db.get_scan(99999) is None


# ── update_scan ────────────────────────────────────────────────────────────────

def test_update_status_done(fresh):
    sid = db.insert_scan(name="upd", images_dir="x", workspace="y")
    db.update_scan(sid, status="done", ply_path="/pc.ply", elapsed_sec=12.5)
    s = db.get_scan(sid)
    assert s["status"] == "done"
    assert s["ply_path"] == "/pc.ply"
    assert s["elapsed_sec"] == pytest.approx(12.5)


def test_update_error(fresh):
    sid = db.insert_scan(name="err", images_dir="x", workspace="y")
    db.update_scan(sid, status="error", error_msg="COLMAP failed")
    s = db.get_scan(sid)
    assert s["status"] == "error"
    assert "COLMAP" in s["error_msg"]


def test_update_empty_kwargs_noop(fresh):
    sid = db.insert_scan(name="noop", images_dir="x", workspace="y")
    db.update_scan(sid)  # пустой вызов — не должен падать
    assert db.get_scan(sid)["status"] == "running"


def test_update_nonexistent_noop(fresh):
    db.update_scan(99999, status="done")  # не должен падать


# ── get_all_scans ──────────────────────────────────────────────────────────────

def test_get_all_empty(fresh):
    assert db.get_all_scans() == []


def test_get_all_descending_order(fresh):
    db.insert_scan(name="first",  images_dir="a", workspace="a")
    db.insert_scan(name="second", images_dir="b", workspace="b")
    scans = db.get_all_scans()
    assert len(scans) == 2
    assert scans[0]["name"] == "second"  # DESC — новые первыми


def test_get_all_returns_all(fresh):
    for i in range(5):
        db.insert_scan(name=f"s{i}", images_dir="x", workspace="y")
    assert len(db.get_all_scans()) == 5


# ── get_last_done_scan ─────────────────────────────────────────────────────────

def test_last_done_none_when_empty(fresh):
    assert db.get_last_done_scan() is None


def test_last_done_ignores_errors(fresh):
    sid = db.insert_scan(name="err", images_dir="x", workspace="y")
    db.update_scan(sid, status="error")
    assert db.get_last_done_scan() is None


def test_last_done_returns_newest(fresh):
    s1 = db.insert_scan(name="old", images_dir="x", workspace="y")
    db.update_scan(s1, status="done", ply_path="/old.ply")
    s2 = db.insert_scan(name="new", images_dir="x", workspace="y")
    db.update_scan(s2, status="done", ply_path="/new.ply")
    assert db.get_last_done_scan()["name"] == "new"


# ── delete_scan ────────────────────────────────────────────────────────────────

def test_delete_removes_record(fresh):
    sid = db.insert_scan(name="del", images_dir="x", workspace="y")
    db.delete_scan(sid)
    assert db.get_scan(sid) is None


def test_delete_nonexistent_noop(fresh):
    db.delete_scan(99999)  # не должен падать


def test_delete_does_not_affect_others(fresh):
    s1 = db.insert_scan(name="keep", images_dir="x", workspace="y")
    s2 = db.insert_scan(name="del",  images_dir="x", workspace="y")
    db.delete_scan(s2)
    assert db.get_scan(s1) is not None
