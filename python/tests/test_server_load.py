"""Интеграционные тесты /api/scans и /api/scans/{id}/load через TestClient.

ВАЖНО: SCANNER_DB должен быть установлен ДО импорта api.server,
потому что server.py вызывает init_db() на уровне модуля.
Здесь это делается через os.environ до первого импорта.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# ── Тестовая БД — должна быть настроена ДО импорта server ─────────────────────
_TMP = Path(tempfile.mkdtemp())
os.environ["SCANNER_DB"] = str(_TMP / "test_server.db")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import api.db as db
from fastapi.testclient import TestClient
from api.server import app, _put   # noqa: E402 (после env-setup)

client = TestClient(app)


# ── Вспомогательная функция ────────────────────────────────────────────────────

def _make_ply(name: str = "cloud.ply") -> Path:
    """Минимальный валидный ASCII PLY (3 вершины)."""
    p = _TMP / name
    p.write_bytes(
        b"ply\nformat ascii 1.0\n"
        b"element vertex 3\n"
        b"property float x\nproperty float y\nproperty float z\n"
        b"end_header\n0 0 0\n1 0 0\n0 1 0\n"
    )
    return p


def _done_scan(name: str, ply: Path, images_dir: str = "D:/photos") -> int:
    """Вставить скан со статусом done и заданным PLY."""
    sid = db.insert_scan(name=name, images_dir=images_dir, workspace=str(_TMP))
    db.update_scan(sid, status="done", ply_path=str(ply))
    return sid


# ── GET /api/scans ─────────────────────────────────────────────────────────────

class TestListScans:
    def test_returns_list(self):
        r = client.get("/api/scans")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_inserted_scan_appears(self):
        db.insert_scan(name="visible_scan", images_dir="x", workspace="y")
        names = [s["name"] for s in client.get("/api/scans").json()]
        assert "visible_scan" in names

    def test_newest_first(self):
        db.insert_scan(name="scan_aaa", images_dir="x", workspace="y")
        db.insert_scan(name="scan_zzz", images_dir="x", workspace="y")
        scans = client.get("/api/scans").json()
        names = [s["name"] for s in scans]
        assert names.index("scan_zzz") < names.index("scan_aaa")


# ── POST /api/scans/{id}/load ──────────────────────────────────────────────────

class TestLoadScan:
    def test_not_found(self):
        assert client.post("/api/scans/99999/load").status_code == 404

    def test_wrong_status_running(self):
        sid = db.insert_scan(name="still_running", images_dir="x", workspace="y")
        assert client.post(f"/api/scans/{sid}/load").status_code == 400

    def test_wrong_status_error(self):
        sid = db.insert_scan(name="failed", images_dir="x", workspace="y")
        db.update_scan(sid, status="error")
        assert client.post(f"/api/scans/{sid}/load").status_code == 400

    def test_ply_missing_on_disk(self):
        sid = db.insert_scan(name="ghost", images_dir="x", workspace="y")
        db.update_scan(sid, status="done", ply_path="/nonexistent/pc.ply")
        assert client.post(f"/api/scans/{sid}/load").status_code == 404

    def test_success_returns_ok(self):
        ply = _make_ply("load_ok.ply")
        sid = _done_scan("load_ok", ply, images_dir="D:/mug")
        r   = client.post(f"/api/scans/{sid}/load")
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_images_dir_in_response(self):
        ply = _make_ply("imgdir.ply")
        sid = _done_scan("imgdir_scan", ply, images_dir="D:/cup")
        r   = client.post(f"/api/scans/{sid}/load")
        assert r.json()["images_dir"] == "D:/cup"

    def test_state_updated_after_load(self):
        ply = _make_ply("state_check.ply")
        sid = _done_scan("state_check", ply, images_dir="D:/thing")
        client.post(f"/api/scans/{sid}/load")

        st = client.get("/api/status").json()
        assert st["status"] == "done"
        assert st["result_ply"] == str(ply)
        assert st["scan_id"] == sid
        assert st["images_dir"] == "D:/thing"


# ── DELETE /api/scans/{id} ─────────────────────────────────────────────────────

class TestDeleteScan:
    def test_delete_existing(self):
        sid = db.insert_scan(name="to_del", images_dir="x", workspace="y")
        r   = client.delete(f"/api/scans/{sid}")
        assert r.status_code == 200
        assert db.get_scan(sid) is None

    def test_delete_not_found(self):
        assert client.delete("/api/scans/88888").status_code == 404

    def test_delete_does_not_affect_others(self):
        s1 = db.insert_scan(name="keep",   images_dir="x", workspace="y")
        s2 = db.insert_scan(name="remove", images_dir="x", workspace="y")
        client.delete(f"/api/scans/{s2}")
        assert db.get_scan(s1) is not None
