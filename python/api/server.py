"""FastAPI: локальный сервер 3D-сканера, порт 8765."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Пути ──────────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_WEB_DIR      = _PROJECT_ROOT / "web"
_DATA_DIR     = _PROJECT_ROOT / "data" / "results"
_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Файл-лог ──────────────────────────────────────────────────────────────────
_log_path = _DATA_DIR / f"pipeline_{time.strftime('%Y%m%d_%H%M%S')}.log"
_fh = logging.FileHandler(_log_path, encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt="%H:%M:%S"
))
_root = logging.getLogger()
_root.addHandler(_fh)
_root.setLevel(logging.DEBUG)
# Убрать шум uvicorn access-лога из файла (запросы к /api/...)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ── Глобальный state ───────────────────────────────────────────────────────────
_lock = threading.Lock()
_state: dict = {
    "status":      "idle",   # idle | running | done | error
    "step":        "",
    "progress":    0.0,
    "result_ply":  None,     # str | None — путь к point_cloud_clean.ply
    "result_mesh": None,     # str | None — путь к mesh_fixed/repaired.ply
    "images_dir":  None,     # str | None — папка с оригинальными фото
    "scan_id":     None,     # int | None — id записи в БД
    "error":       None,
}


def _get() -> dict:
    with _lock:
        return dict(_state)


def _put(**kw) -> None:
    with _lock:
        _state.update(kw)


# ── БД: инициализация и восстановление последнего скана ───────────────────────
from api.db import (                                          # noqa: E402
    init_db      as _db_init,
    insert_scan  as _db_insert,
    update_scan  as _db_update,
    get_scan     as _db_get_scan,
    get_all_scans       as _db_get_all,
    get_last_done_scan  as _db_last_done,
    delete_scan  as _db_delete,
)

_DB_FILE = Path(os.environ.get("SCANNER_DB", str(_DATA_DIR / "scans.db")))
_db_init(_DB_FILE)

_last_scan = _db_last_done()
if _last_scan and _last_scan.get("ply_path") and Path(_last_scan["ply_path"]).exists():
    _put(
        status="done", step="done", progress=1.0,
        result_ply  = _last_scan["ply_path"],
        result_mesh = _last_scan.get("mesh_path"),
        images_dir  = _last_scan.get("images_dir"),
        scan_id     = _last_scan["id"],
    )
    logger.info("Restored scan #%d: %s", _last_scan["id"], _last_scan["name"])


# ── FastAPI ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Scanner API", version="0.1.0")


# ── Фоновый пайплайн ──────────────────────────────────────────────────────────

def _find_mesh(workspace: Path) -> Path | None:
    """Искать mesh_fixed.ply, затем mesh_repaired.ply в workspace/mesh/."""
    for name in ("mesh_fixed.ply", "mesh_repaired.ply"):
        p = workspace / "mesh" / name
        if p.exists():
            return p
    return None


def _pipeline_thread(images_dir: Path, output_path: Path, scan_id: int,
                     quality: str = "medium") -> None:
    """Запускается в daemon-потоке: полный пайплайн сканирования."""
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    from scanner.config import ScanConfig
    from scanner.pipeline import ScanPipeline

    def _cb(step: str, progress: float) -> None:
        _put(step=step, progress=progress)

    try:
        cfg = ScanConfig(**_QUALITY_PRESETS.get(quality, {}))
        result = ScanPipeline(cfg).scan(
            images_dir, output_path, progress_callback=_cb,
        )
        ws        = result.workspace
        ply_path  = ws / "mesh" / "point_cloud_clean.ply"
        mesh_path = _find_mesh(ws)

        ply_str  = str(ply_path)  if ply_path.exists() else None
        mesh_str = str(mesh_path) if mesh_path         else None

        _put(
            status="done", step="done", progress=1.0,
            result_ply=ply_str, result_mesh=mesh_str,
        )
        _db_update(
            scan_id,
            workspace   = str(ws),
            ply_path    = ply_str,
            mesh_path   = mesh_str,
            status      = "done",
            n_images    = result.n_images,
            elapsed_sec = result.elapsed_seconds,
        )
        logger.info("Pipeline done → %s", output_path)

    except Exception as exc:
        logger.exception("Pipeline error")
        _put(status="error", error=str(exc))
        _db_update(scan_id, status="error", error_msg=str(exc))


# ── Эндпоинты ─────────────────────────────────────────────────────────────────

class StartBody(BaseModel):
    images_dir: str
    quality: str = "medium"   # low | medium | high


# Карта качества → параметры ScanConfig
_QUALITY_PRESETS: dict[str, dict] = {
    "low":    {"poisson_depth": 7},
    "medium": {"poisson_depth": 9},
    "high":   {"poisson_depth": 11},
}


@app.post("/api/scan/start")
def scan_start(body: StartBody):
    if _get()["status"] == "running":
        raise HTTPException(409, "Pipeline already running")

    images_dir = Path(body.images_dir)
    if not images_dir.exists():
        raise HTTPException(400, f"Directory not found: {images_dir}")

    quality = body.quality if body.quality in _QUALITY_PRESETS else "medium"
    ts          = time.strftime("%Y%m%d_%H%M%S")
    output_path = _DATA_DIR / f"scan_{ts}.stl"
    scan_id     = _db_insert(name=f"scan_{ts}", images_dir=str(images_dir))

    _put(status="running", step="", progress=0.0,
         result_ply=None, result_mesh=None, error=None,
         images_dir=str(images_dir), scan_id=scan_id)

    threading.Thread(
        target=_pipeline_thread,
        args=(images_dir, output_path, scan_id, quality),
        daemon=True,
    ).start()

    logger.info("Pipeline started: %s (scan_id=%d, quality=%s)", images_dir, scan_id, quality)
    return {"ok": True}


# ── История сканов ─────────────────────────────────────────────────────────────

@app.get("/api/scans")
def list_scans():
    return _db_get_all()


@app.post("/api/scans/{scan_id}/load")
def load_scan(scan_id: int):
    scan = _db_get_scan(scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    if scan["status"] != "done":
        raise HTTPException(400, f"Scan status is '{scan['status']}', expected 'done'")
    ply = scan.get("ply_path")
    if not ply or not Path(ply).exists():
        raise HTTPException(404, "PLY file not found on disk")
    _put(
        status="done", step="done", progress=1.0,
        result_ply  = ply,
        result_mesh = scan.get("mesh_path"),
        images_dir  = scan.get("images_dir"),
        scan_id     = scan_id,
        error       = None,
    )
    logger.info("Loaded scan #%d: %s", scan_id, scan.get("name", ""))
    return {"ok": True, "images_dir": scan.get("images_dir")}


@app.delete("/api/scans/{scan_id}")
def delete_scan_endpoint(scan_id: int):
    if not _db_get_scan(scan_id):
        raise HTTPException(404, "Scan not found")
    _db_delete(scan_id)
    return {"ok": True}


@app.get("/api/logs")
def get_server_logs(n: int = 300):
    """Последние N строк из лог-файла сервера."""
    try:
        text  = _log_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        return {"lines": lines[-n:], "file": _log_path.name}
    except Exception:
        return {"lines": [], "file": ""}


@app.get("/api/scan/stream")
async def scan_stream():
    """SSE: шлёт {step, progress, status} каждые 0.5 сек до done/error."""
    async def _generate():
        while True:
            st = _get()
            payload: dict = {
                "step":     st["step"],
                "progress": st["progress"],
                "status":   st["status"],
            }
            if st["status"] == "done":
                payload["result_ply"]  = st["result_ply"]
                payload["result_mesh"] = st["result_mesh"]
            elif st["status"] == "error":
                payload["error"] = st["error"]

            yield f"data: {json.dumps(payload)}\n\n"

            if st["status"] in ("done", "error"):
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(_generate(), media_type="text/event-stream")


@app.get("/api/result/ply")
def result_ply():
    path = _get().get("result_ply")
    if not path or not Path(path).exists():
        raise HTTPException(404, "PLY not ready")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename="point_cloud_clean.ply",
    )


@app.get("/api/result/mesh")
def result_mesh():
    path = _get().get("result_mesh")
    if not path or not Path(path).exists():
        raise HTTPException(404, "Mesh not ready")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename="mesh.ply",
    )


@app.get("/api/status")
def api_status():
    return _get()


# ── Orient ────────────────────────────────────────────────────────────────────

def _current_mesh_path() -> Path | None:
    """Текущий меш для редактирования: oriented → fixed → repaired."""
    mesh_str = _get().get("result_mesh")
    if not mesh_str:
        return None
    base = Path(mesh_str)
    oriented = base.parent / "mesh_oriented.ply"
    if oriented.exists():
        return oriented
    return base if base.exists() else None


@app.post("/api/edit/auto-orient")
def auto_orient():
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    from scanner import PrintPreparation, TriangleMesh

    mesh = TriangleMesh()
    if not mesh.load_ply(str(mesh_path)):
        raise HTTPException(500, f"Cannot load mesh: {mesh_path}")

    PrintPreparation(mesh).auto_orient()

    out = mesh_path.parent / "mesh_oriented.ply"
    if not mesh.save_ply(str(out)):
        raise HTTPException(500, "Cannot save oriented mesh")

    logger.info("auto_orient → %s", out.name)
    return {"ok": True}


class TransformBody(BaseModel):
    matrix: list[float]  # 16 float, column-major (Three.js Matrix4.elements)


@app.post("/api/edit/apply-transform")
def apply_transform(body: TransformBody):
    if len(body.matrix) != 16:
        raise HTTPException(400, "matrix must have exactly 16 elements")

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    import numpy as np
    try:
        import trimesh as tm
    except ImportError:
        raise HTTPException(500, "trimesh not installed")

    try:
        loaded = tm.load(str(mesh_path), force="mesh", process=False)
        v = np.asarray(loaded.vertices, dtype=np.float64)
        f = np.asarray(loaded.faces,    dtype=np.int32)

        if len(f) == 0:
            raise ValueError(f"Mesh has no faces: {mesh_path}")

        # Three.js column-major → правильная 4×4 матрица трансформации
        M = np.array(body.matrix, dtype=np.float64).reshape(4, 4).T
        ones = np.ones((len(v), 1), dtype=np.float64)
        v_new = (M @ np.hstack([v, ones]).T).T[:, :3]

        result = tm.Trimesh(vertices=v_new, faces=f, process=False)

        out = mesh_path.parent / "mesh_oriented.ply"
        result.export(str(out))
    except Exception as exc:
        logger.exception("apply_transform error (mesh=%s)", mesh_path)
        raise HTTPException(500, str(exc))

    logger.info("apply_transform → %s (%d verts)", out.name, len(v_new))
    return {"ok": True}


# ── Denoise ───────────────────────────────────────────────────────────────────

class DeletePointsBody(BaseModel):
    indices: list[int]


@app.post("/api/edit/delete-points")
def delete_points(body: DeletePointsBody):
    import sys
    import numpy as np
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    ply_str = _get().get("result_ply")
    if not ply_str or not Path(ply_str).exists():
        raise HTTPException(404, "Point cloud not available")

    if not body.indices:
        return {"ok": True, "remaining": -1}

    from scanner import PointCloud

    ply_path = Path(ply_str)
    pc = PointCloud()
    if not pc.load_ply(str(ply_path)):
        raise HTTPException(500, f"Cannot load PLY: {ply_path}")

    pts = np.asarray(pc.points, dtype=np.float64)
    n   = len(pts)

    mask = np.ones(n, dtype=bool)
    valid = [i for i in body.indices if 0 <= i < n]
    if valid:
        mask[valid] = False

    pc.points = pts[mask]
    norms = np.asarray(pc.normals)
    if len(norms) == n:
        pc.normals = norms[mask]
    cols = np.asarray(pc.colors)
    if len(cols) == n:
        pc.colors = cols[mask]

    pc.estimate_normals(k=30)

    if not pc.save_ply(str(ply_path)):
        raise HTTPException(500, "Cannot save PLY")

    remaining = int(mask.sum())
    logger.info("delete_points: %d → %d pts (removed %d)", n, remaining, n - remaining)
    return {"ok": True, "remaining": remaining}


def _remesh_thread(ply_path: Path) -> None:
    """Поиссон + ремонт + pymeshfix по текущему point_cloud_clean.ply."""
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    from scanner.config import ScanConfig
    from scanner.mesh_processor import MeshProcessor

    try:
        workspace = ply_path.parent
        repaired  = MeshProcessor(ScanConfig()).process_cloud(
            ply_path, workspace, skip_noise_removal=True
        )

        # Удалить старый mesh_oriented.ply — иначе _current_mesh_path()
        # всегда вернёт его вместо нового mesh_fixed.ply
        oriented_old = repaired.parent / "mesh_oriented.ply"
        if oriented_old.exists():
            oriented_old.unlink()
            logger.info("Deleted stale mesh_oriented.ply")

        new_clean = workspace / "point_cloud_clean.ply"
        _put(
            status="done",
            step="done",
            progress=1.0,
            result_ply=str(new_clean) if new_clean.exists() else str(ply_path),
            result_mesh=str(repaired),
        )
        logger.info("Remesh done → %s", repaired.name)

    except Exception as exc:
        logger.exception("Remesh error")
        _put(status="error", error=str(exc))


@app.post("/api/edit/remesh")
def remesh():
    st = _get()
    if st["status"] == "running":
        raise HTTPException(409, "Already running")

    ply_str = st.get("result_ply")
    if not ply_str or not Path(ply_str).exists():
        raise HTTPException(404, "No point cloud available")

    _put(status="running", step="remesh", progress=0.0, error=None)

    threading.Thread(
        target=_remesh_thread,
        args=(Path(ply_str),),
        daemon=True,
    ).start()

    logger.info("Remesh started: %s", ply_str)
    return {"ok": True}


@app.get("/api/result/oriented")
def result_oriented():
    mesh_str = _get().get("result_mesh")
    if not mesh_str:
        raise HTTPException(404, "No mesh available")

    base     = Path(mesh_str)
    oriented = base.parent / "mesh_oriented.ply"
    path     = oriented if oriented.exists() else base

    if not path.exists():
        raise HTTPException(404, "Mesh file not found")

    return FileResponse(
        str(path),
        media_type="application/octet-stream",
        filename="mesh_oriented.ply",
    )


# ── Export state ──────────────────────────────────────────────────────────────

_export_lock  = threading.Lock()
_export_state: dict = {
    "status":   "idle",   # idle | running | done | error
    "step":     "",
    "progress": 0.0,
    "stl_path": None,
    "zip_path": None,
    "error":    None,
}


def _eget() -> dict:
    with _export_lock:
        return dict(_export_state)


def _eput(**kw) -> None:
    with _export_lock:
        _export_state.update(kw)


# ── Export: STL ────────────────────────────────────────────────────────────────

class ExportStlBody(BaseModel):
    height_mm: float = 100.0
    add_base: bool   = False


@app.post("/api/export/stl")
def export_stl(body: ExportStlBody):
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    from scanner.config import ScanConfig
    from scanner.exporter import Exporter

    cfg = ScanConfig()
    cfg.target_height_mm = body.height_mm
    cfg.add_base         = body.add_base
    cfg.auto_orient      = False  # пользователь уже ориентировал в редакторе

    out = _DATA_DIR / f"export_{time.strftime('%Y%m%d_%H%M%S')}.stl"
    try:
        result = Exporter(cfg).prepare_and_export(mesh_path, out)
    except Exception as exc:
        logger.exception("STL export error")
        raise HTTPException(500, str(exc))

    _eput(stl_path=str(result.output_path))
    logger.info("export_stl → %s (%.1f KB)", out.name, out.stat().st_size / 1024)
    return {"ok": True}


@app.get("/api/export/download/stl")
def download_stl():
    path = _eget().get("stl_path")
    if not path or not Path(path).exists():
        raise HTTPException(404, "STL not ready")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename="model.stl",
        headers={"Content-Disposition": "attachment; filename=model.stl"},
    )


# ── Export: OBJ + texture ─────────────────────────────────────────────────────

class ExportObjBody(BaseModel):
    images_dir: str


def _obj_thread(images_dir: Path) -> None:
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    ply_str = _get().get("result_ply")
    if not ply_str or not Path(ply_str).exists():
        _eput(status="error", error="Point cloud не найден — запустите сканирование")
        return

    workspace = Path(ply_str).parent.parent  # workspace/mesh/file.ply → workspace

    from scanner.config import ScanConfig
    from scanner.colmap_runner import ColmapRunner

    def _cb(step: str, progress: float) -> None:
        _eput(step=step, progress=progress)

    try:
        zip_path = ColmapRunner(ScanConfig()).texture_export(images_dir, workspace, _cb)
        _eput(status="done", step="done", progress=1.0, zip_path=str(zip_path))
        logger.info("OBJ texture export done → %s", zip_path.name)
    except Exception as exc:
        logger.exception("OBJ texture export error")
        _eput(status="error", error=str(exc))


@app.post("/api/export/obj-texture")
def export_obj_texture(body: ExportObjBody):
    if _eget()["status"] == "running":
        raise HTTPException(409, "Export already running")

    images_dir = Path(body.images_dir)
    if not images_dir.exists():
        raise HTTPException(400, f"Directory not found: {images_dir}")

    _eput(status="running", step="", progress=0.0, zip_path=None, error=None)

    threading.Thread(
        target=_obj_thread,
        args=(images_dir,),
        daemon=True,
    ).start()

    logger.info("OBJ texture export started: %s", images_dir)
    return {"ok": True}


@app.get("/api/export/stream")
async def export_stream():
    """SSE: прогресс экспорта OBJ+текстура."""
    async def _gen():
        while True:
            st = _eget()
            payload: dict = {
                "step":     st["step"],
                "progress": st["progress"],
                "status":   st["status"],
            }
            if st["status"] == "error":
                payload["error"] = st["error"]
            yield f"data: {json.dumps(payload)}\n\n"
            if st["status"] in ("done", "error"):
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(_gen(), media_type="text/event-stream")


@app.get("/api/export/download/obj")
def download_obj():
    path = _eget().get("zip_path")
    if not path or not Path(path).exists():
        raise HTTPException(404, "ZIP not ready")
    return FileResponse(
        path,
        media_type="application/zip",
        filename="texture_export.zip",
        headers={"Content-Disposition": "attachment; filename=texture_export.zip"},
    )


# ── Repair ────────────────────────────────────────────────────────────────────

@app.get("/api/edit/mesh-info")
def mesh_info():
    import numpy as np
    try:
        import trimesh as tm
    except ImportError:
        raise HTTPException(500, "trimesh not installed")

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    m = tm.load(str(mesh_path), force="mesh", process=False)

    unique, counts = np.unique(m.edges_sorted, axis=0, return_counts=True)
    n_open = int(np.sum(counts == 1))

    return {
        "vertices":     len(m.vertices),
        "faces":        len(m.faces),
        "open_edges":   n_open,
        "is_watertight": bool(m.is_watertight),
        "volume_mm3":   float(abs(m.volume)) if m.is_watertight else 0.0,
    }


@app.get("/api/result/boundary-edges")
def boundary_edges():
    import numpy as np
    try:
        import trimesh as tm
    except ImportError:
        raise HTTPException(500, "trimesh not installed")

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    m = tm.load(str(mesh_path), force="mesh", process=False)

    unique, counts = np.unique(m.edges_sorted, axis=0, return_counts=True)
    boundary = unique[counts == 1]  # (N, 2) vertex indices

    if len(boundary) == 0:
        return {"edges": []}

    boundary = boundary[:10_000]
    v1 = m.vertices[boundary[:, 0]]
    v2 = m.vertices[boundary[:, 1]]
    return {"edges": np.hstack([v1, v2]).tolist()}


@app.post("/api/edit/fill-holes")
def fill_holes():
    import numpy as np
    try:
        import trimesh as tm
        import pymeshfix
    except ImportError as exc:
        raise HTTPException(500, str(exc))

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    try:
        m = tm.load(str(mesh_path), force="mesh", process=False)
        if len(m.faces) == 0:
            raise ValueError(f"Mesh has no faces: {mesh_path}")

        tm.repair.fill_holes(m)

        mf = pymeshfix.MeshFix(
            np.array(m.vertices, dtype=np.float64),
            np.array(m.faces,    dtype=np.int32),
        )
        mf.repair()
        result = tm.Trimesh(vertices=mf.v, faces=mf.f, process=False)

        out = mesh_path.parent / "mesh_oriented.ply"
        result.export(str(out))
    except Exception as exc:
        logger.exception("fill_holes error (mesh=%s)", mesh_path)
        raise HTTPException(500, str(exc))

    logger.info("fill_holes → %s (%d faces)", out.name, len(result.faces))
    return {"ok": True, "faces": len(result.faces)}


@app.post("/api/edit/smooth")
def smooth_mesh(iterations: int = 3):
    try:
        import trimesh as tm
        import trimesh.smoothing
    except ImportError as exc:
        raise HTTPException(500, str(exc))

    mesh_path = _current_mesh_path()
    if not mesh_path:
        raise HTTPException(404, "No mesh available")

    try:
        m = tm.load(str(mesh_path), force="mesh", process=False)
        if len(m.faces) == 0:
            raise ValueError(f"Mesh has no faces: {mesh_path}")
        tm.smoothing.filter_laplacian(m, iterations=iterations)
        out = mesh_path.parent / "mesh_oriented.ply"
        m.export(str(out))
    except Exception as exc:
        logger.exception("smooth error (mesh=%s)", mesh_path)
        raise HTTPException(500, str(exc))

    logger.info("smooth → %s (%d iters)", out.name, iterations)
    return {"ok": True}


# ── Статика — монтируем последней, чтобы не перекрывать API ───────────────────
if _WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_WEB_DIR), html=True), name="web")
