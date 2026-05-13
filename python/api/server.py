"""FastAPI: локальный сервер 3D-сканера, порт 8765."""
from __future__ import annotations

import asyncio
import json
import logging
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
_log_path = _DATA_DIR / f"server_{time.strftime('%Y%m%d_%H%M%S')}.log"
_fh = logging.FileHandler(_log_path, encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt="%H:%M:%S"
))
logging.getLogger().addHandler(_fh)
logger = logging.getLogger(__name__)

# ── Глобальный state ───────────────────────────────────────────────────────────
_lock = threading.Lock()
_state: dict = {
    "status":      "idle",   # idle | running | done | error
    "step":        "",
    "progress":    0.0,
    "result_ply":  None,     # str | None — путь к point_cloud_clean.ply
    "result_mesh": None,     # str | None — путь к mesh_fixed/repaired.ply
    "error":       None,
}


def _get() -> dict:
    with _lock:
        return dict(_state)


def _put(**kw) -> None:
    with _lock:
        _state.update(kw)


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


def _pipeline_thread(images_dir: Path, output_path: Path) -> None:
    """Запускается в daemon-потоке: полный пайплайн сканирования."""
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "python"))

    from scanner.config import ScanConfig
    from scanner.pipeline import ScanPipeline

    def _cb(step: str, progress: float) -> None:
        _put(step=step, progress=progress)

    try:
        result = ScanPipeline(ScanConfig()).scan(
            images_dir, output_path, progress_callback=_cb
        )
        ws       = result.workspace
        ply_path = ws / "mesh" / "point_cloud_clean.ply"
        mesh_path = _find_mesh(ws)

        _put(
            status="done",
            step="done",
            progress=1.0,
            result_ply=str(ply_path) if ply_path.exists() else None,
            result_mesh=str(mesh_path) if mesh_path else None,
        )
        logger.info("Pipeline done → %s", output_path)

    except Exception as exc:
        logger.exception("Pipeline error")
        _put(status="error", error=str(exc))


# ── Эндпоинты ─────────────────────────────────────────────────────────────────

class StartBody(BaseModel):
    images_dir: str


@app.post("/api/scan/start")
def scan_start(body: StartBody):
    if _get()["status"] == "running":
        raise HTTPException(409, "Pipeline already running")

    images_dir = Path(body.images_dir)
    if not images_dir.exists():
        raise HTTPException(400, f"Directory not found: {images_dir}")

    output_path = _DATA_DIR / f"scan_{time.strftime('%Y%m%d_%H%M%S')}.stl"

    _put(status="running", step="", progress=0.0,
         result_ply=None, result_mesh=None, error=None)

    threading.Thread(
        target=_pipeline_thread,
        args=(images_dir, output_path),
        daemon=True,
    ).start()

    logger.info("Pipeline started: %s", images_dir)
    return {"ok": True}


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

    loaded = tm.load(str(mesh_path), force="mesh", process=False)
    v = np.asarray(loaded.vertices, dtype=np.float64)
    f = np.asarray(loaded.faces,    dtype=np.int32)

    # Three.js column-major → правильная 4×4 матрица трансформации
    M = np.array(body.matrix, dtype=np.float64).reshape(4, 4).T
    ones = np.ones((len(v), 1), dtype=np.float64)
    v_new = (M @ np.hstack([v, ones]).T).T[:, :3]

    result = tm.Trimesh(vertices=v_new, faces=f, process=False)
    result.compute_vertex_normals()

    out = mesh_path.parent / "mesh_oriented.ply"
    result.export(str(out))

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
        repaired  = MeshProcessor(ScanConfig()).process_cloud(ply_path, workspace)

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


# ── Статика — монтируем последней, чтобы не перекрывать API ───────────────────
if _WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_WEB_DIR), html=True), name="web")
