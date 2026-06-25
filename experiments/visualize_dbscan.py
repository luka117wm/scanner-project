"""
visualize_dbscan.py — Рисунок 1.6 диплома.

Запускает мини-сервер → открывает браузер → Three.js рендер:
  Левая панель  : fused.ply (нейтральный серый)
  Правая панель : результат SOR + ROR + DBSCAN
    Синий  = объект (наибольший кластер)
    Красный = шум / фон
    Серый  = малые кластеры

Запуск:
    python experiments/visualize_dbscan.py
    python experiments/visualize_dbscan.py path/to/fused.ply
    python experiments/visualize_dbscan.py fused.ply --port 8766 --no-browser
"""
from __future__ import annotations

import re
import sys
import struct
import argparse
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, JSONResponse

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "python"))

# ── Глобальный стейт сервера ──────────────────────────────────────────────────
_state: dict = {}   # заполняется в main() до старта сервера

# ── PLY-загрузчик ─────────────────────────────────────────────────────────────

def _load_ply(path: Path) -> np.ndarray:
    try:
        import open3d as o3d
        pcd = o3d.io.read_point_cloud(str(path))
        pts = np.asarray(pcd.points, dtype=np.float32)
        if len(pts):
            return pts
    except Exception:
        pass

    try:
        from scanner import PointCloud
        pc = PointCloud()
        if pc.load_ply(str(path)):
            pts = np.asarray(pc.points, dtype=np.float32)
            if len(pts):
                return pts
    except Exception:
        pass

    return _read_ply_numpy(path)


def _read_ply_numpy(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        lines: list[str] = []
        while True:
            line = f.readline().decode("utf-8", errors="ignore").rstrip()
            lines.append(line)
            if line == "end_header":
                break
        header = "\n".join(lines)

        m = re.search(r"element vertex (\d+)", header)
        if not m:
            raise RuntimeError(f"'element vertex' не найден в {path}")
        n = int(m.group(1))

        endian = "<" if "binary_little_endian" in header else ">"
        tmap = {"float": "f4", "double": "f8",
                "uchar": "u1", "uint8": "u1",
                "int": "i4", "uint": "u4",
                "short": "i2", "ushort": "u2"}
        sec = re.search(r"element vertex.*?(?=element |\Z)", header, re.DOTALL)
        props = re.findall(r"property (\w+) (\w+)", sec.group() if sec else header)
        dt  = np.dtype([(nm, endian + tmap.get(tp, "f4")) for tp, nm in props])
        arr = np.frombuffer(f.read(n * dt.itemsize), dtype=dt)

    return np.stack([arr["x"].astype("f4"),
                     arr["y"].astype("f4"),
                     arr["z"].astype("f4")], axis=1)


# ── Фильтры ───────────────────────────────────────────────────────────────────

def _sor(pts: np.ndarray, k: int = 20, std_mul: float = 2.0) -> np.ndarray:
    from scipy.spatial import cKDTree
    print(f"  SOR k={k} std={std_mul} ...")
    tree = cKDTree(pts)
    d, _  = tree.query(pts, k=k + 1)
    md    = d[:, 1:].mean(axis=1)
    mask  = md <= (md.mean() + std_mul * md.std())
    print(f"    Удалено: {(~mask).sum():,}")
    return mask


def _ror(pts: np.ndarray, radius: float, min_nb: int = 5) -> np.ndarray:
    from scipy.spatial import cKDTree
    print(f"  ROR radius={radius:.5f} min_nb={min_nb} ...")
    tree  = cKDTree(pts)
    cnt   = tree.query_ball_point(pts, r=radius, return_length=True, workers=-1)
    mask  = np.asarray(cnt, dtype=np.int32) >= (min_nb + 1)
    print(f"    Удалено: {(~mask).sum():,}")
    return mask


def _dbscan(pts: np.ndarray, eps_factor: float = 3.0,
            min_pts: int = 10) -> np.ndarray:
    from sklearn.cluster import DBSCAN
    bbox  = pts.max(0) - pts.min(0)
    eps   = float(np.linalg.norm(bbox)) / np.sqrt(len(pts)) * eps_factor
    print(f"  DBSCAN N={len(pts):,} eps={eps:.5f} min_pts={min_pts} ...")
    lbl = DBSCAN(eps=eps, min_samples=min_pts,
                 algorithm="kd_tree", n_jobs=-1).fit_predict(pts)
    nc  = len(set(lbl)) - (1 if -1 in lbl else 0)
    print(f"    Кластеров: {nc}  шум: {(lbl==-1).sum():,}")
    return lbl


# ── Вычисление меток ──────────────────────────────────────────────────────────

def run_pipeline(ply_path: Path,
                 sor_k: int, sor_std: float,
                 ror_min_nb: int,
                 eps_factor: float, min_pts: int) -> dict:
    print(f"Загружаю: {ply_path}")
    pts = _load_ply(ply_path)
    N   = len(pts)
    print(f"  Точек: {N:,}")
    if N == 0:
        raise RuntimeError("Облако пустое.")

    sor_ok = _sor(pts, k=sor_k, std_mul=sor_std)

    bbox     = pts.max(0) - pts.min(0)
    ror_rad  = float(np.linalg.norm(bbox)) / np.sqrt(N) * 1.5
    ror_ok   = _ror(pts, radius=ror_rad, min_nb=ror_min_nb)

    surv_idx = np.where(sor_ok & ror_ok)[0]
    print(f"  После SOR+ROR: {len(surv_idx):,}")

    lbl = _dbscan(pts[surv_idx], eps_factor=eps_factor, min_pts=min_pts)

    valid = lbl[lbl >= 0]
    if not len(valid):
        raise RuntimeError("DBSCAN не нашёл кластеров.")
    uniq, cnt = np.unique(valid, return_counts=True)
    obj_cl    = int(uniq[np.argmax(cnt)])

    # final: 0=шум/удалён, 1=объект, 2=малый кластер
    final = np.zeros(N, dtype=np.int8)
    final[surv_idx[lbl == obj_cl]]                   = 1
    final[surv_idx[(lbl >= 0) & (lbl != obj_cl)]]   = 2

    n_obj   = int((final == 1).sum())
    n_noise = int((final == 0).sum())
    n_other = int((final == 2).sum())
    print(f"\n  Объект: {n_obj:,} ({n_obj/N*100:.1f}%)  "
          f"Шум: {n_noise:,}  Прочие: {n_other:,}")

    # Цвета (float32 RGB 0..1)
    NEUTRAL = (0.65, 0.65, 0.68)
    BLUE    = (0.22, 0.51, 1.00)
    RED     = (0.92, 0.18, 0.18)
    GRAY    = (0.50, 0.50, 0.52)

    c_before = np.tile(np.float32(NEUTRAL), (N, 1))
    c_after  = np.tile(np.float32(RED),     (N, 1))
    c_after[final == 1] = BLUE
    c_after[final == 2] = GRAY

    # Адаптивный размер точки
    center = pts.mean(0)
    radius = float(np.linalg.norm(pts - center, axis=1).max())
    pt_size = radius * 0.004

    return {
        "pts":      pts,
        "c_before": c_before,
        "c_after":  c_after,
        "n_total":  N,
        "n_obj":    n_obj,
        "n_noise":  n_noise,
        "n_other":  n_other,
        "pct_obj":  round(n_obj / N * 100, 1),
        "pt_size":  round(pt_size, 6),
        "name":     ply_path.name,
    }


# ── Бинарная упаковка (x y z r g b float32 interleaved) ──────────────────────

def _pack(pts: np.ndarray, colors: np.ndarray) -> bytes:
    """Сериализовать облако в бинарный буфер Float32 [x,y,z,r,g,b, ...]."""
    buf = np.empty((len(pts), 6), dtype=np.float32)
    buf[:, :3] = pts
    buf[:, 3:] = colors
    return buf.tobytes()


# ── FastAPI ───────────────────────────────────────────────────────────────────

app = FastAPI()

_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>DBSCAN — {name}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0c0e13;color:#e8eaf0;font-family:'Segoe UI',sans-serif;overflow:hidden}}
#wrap{{display:flex;width:100vw;height:100vh}}
.panel{{flex:1;position:relative;border-right:1px solid #2a2f38}}
.panel:last-child{{border-right:none}}
.lbl{{
  position:absolute;bottom:20px;left:50%;transform:translateX(-50%);
  background:rgba(12,14,19,0.75);padding:7px 16px;border-radius:8px;
  font-size:12px;text-align:center;white-space:nowrap;
  border:1px solid #2a2f38;pointer-events:none;line-height:1.6
}}
.legend{{
  position:absolute;top:14px;left:14px;
  background:rgba(26,30,36,0.92);padding:10px 14px;
  border-radius:8px;border:1px solid #3a3f48;font-size:12px
}}
.li{{display:flex;align-items:center;gap:8px;margin:4px 0}}
.dot{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
#loading{{
  position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  font-size:16px;color:#aaa
}}
</style>
<script type="importmap">
{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.161/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.161/examples/jsm/"}}}}
</script>
</head>
<body>
<div id="loading">Загрузка облака точек…</div>
<div id="wrap" style="display:none">
  <div class="panel" id="pA"><div class="lbl" id="lblA"></div></div>
  <div class="panel" id="pB">
    <div class="lbl" id="lblB"></div>
    <div class="legend">
      <div class="li"><div class="dot" style="background:#3882ff"></div>Объект</div>
      <div class="li"><div class="dot" style="background:#eb2e2e"></div>Шум / фон</div>
      <div class="li"><div class="dot" style="background:#808083"></div>Малые кластеры</div>
    </div>
  </div>
</div>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

async function fetchCloud(url){{
  const r = await fetch(url);
  return new Float32Array(await r.arrayBuffer());
}}

function buildCloud(data){{
  const n = data.length/6;
  const pos = new Float32Array(n*3);
  const col = new Float32Array(n*3);
  for(let i=0;i<n;i++){{
    pos[i*3]=data[i*6]; pos[i*3+1]=data[i*6+1]; pos[i*3+2]=data[i*6+2];
    col[i*3]=data[i*6+3]; col[i*3+1]=data[i*6+4]; col[i*3+2]=data[i*6+5];
  }}
  const g = new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('color',   new THREE.BufferAttribute(col,3));
  g.computeBoundingSphere();
  return g;
}}

function makeView(container, geo, ptSize){{
  const w=container.clientWidth, h=container.clientHeight;
  const scene    = new THREE.Scene();
  scene.background = new THREE.Color(0x0c0e13);
  const camera   = new THREE.PerspectiveCamera(45,w/h,0.0001,10000);
  const renderer = new THREE.WebGLRenderer({{antialias:false}});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.setSize(w,h);
  container.appendChild(renderer.domElement);
  const ctrl = new OrbitControls(camera,renderer.domElement);
  ctrl.enableDamping=true; ctrl.dampingFactor=0.08;
  const mat  = new THREE.PointsMaterial({{size:ptSize,vertexColors:true,sizeAttenuation:true}});
  scene.add(new THREE.Points(geo,mat));
  const c = geo.boundingSphere.center, r = geo.boundingSphere.radius;
  camera.position.set(c.x, c.y+r*0.2, c.z+r*2.5);
  ctrl.target.copy(c); ctrl.update();
  new ResizeObserver(()=>{{
    camera.aspect=container.clientWidth/container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth,container.clientHeight);
  }}).observe(container);
  return {{scene,camera,renderer,ctrl}};
}}

async function main(){{
  const [info,dA,dB] = await Promise.all([
    fetch('/api/info').then(r=>r.json()),
    fetchCloud('/api/before'),
    fetchCloud('/api/after'),
  ]);
  document.getElementById('loading').style.display='none';
  document.getElementById('wrap').style.display='flex';

  const fmt = n=>n.toLocaleString('ru-RU');
  document.getElementById('lblA').innerHTML =
    `До фильтрации (fused.ply)<br>${{fmt(info.n_total)}} точек`;
  document.getElementById('lblB').innerHTML =
    `После SOR + ROR + DBSCAN<br>`+
    `Объект: ${{fmt(info.n_obj)}} (${{info.pct_obj}}%) · `+
    `Шум: ${{fmt(info.n_noise)}} · Прочие: ${{fmt(info.n_other)}}`;

  const geoA = buildCloud(dA);
  const geoB = buildCloud(dB);
  const ps   = info.pt_size;
  const A = makeView(document.getElementById('pA'), geoA, ps);
  const B = makeView(document.getElementById('pB'), geoB, ps);

  let syncLock = false;
  function syncAtoB(){{
    if(syncLock) return; syncLock=true;
    B.camera.position.copy(A.camera.position);
    B.camera.quaternion.copy(A.camera.quaternion);
    B.ctrl.target.copy(A.ctrl.target);
    B.ctrl.update(); syncLock=false;
  }}
  function syncBtoA(){{
    if(syncLock) return; syncLock=true;
    A.camera.position.copy(B.camera.position);
    A.camera.quaternion.copy(B.camera.quaternion);
    A.ctrl.target.copy(B.ctrl.target);
    A.ctrl.update(); syncLock=false;
  }}
  A.ctrl.addEventListener('change', syncAtoB);
  B.ctrl.addEventListener('change', syncBtoA);

  (function animate(){{
    requestAnimationFrame(animate);
    A.ctrl.update(); B.ctrl.update();
    A.renderer.render(A.scene,A.camera);
    B.renderer.render(B.scene,B.camera);
  }})();
}}
main();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return _HTML.format(name=_state.get("name", "fused.ply"))


@app.get("/api/info")
async def info():
    return JSONResponse({k: _state[k] for k in
                         ("n_total","n_obj","n_noise","n_other","pct_obj","pt_size","name")})


@app.get("/api/before")
async def before():
    data = _pack(_state["pts"], _state["c_before"])
    return Response(content=data, media_type="application/octet-stream")


@app.get("/api/after")
async def after():
    data = _pack(_state["pts"], _state["c_after"])
    return Response(content=data, media_type="application/octet-stream")


# ── Точка входа ───────────────────────────────────────────────────────────────

def _pick_file() -> Path | None:
    root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
    p = filedialog.askopenfilename(
        title="Выберите fused.ply",
        initialdir=str(_ROOT / "data"),
        filetypes=[("PLY", "*.ply"), ("Все", "*.*")],
    )
    root.destroy()
    return Path(p) if p else None


def main() -> None:
    parser = argparse.ArgumentParser(description="DBSCAN визуализатор (Рисунок 1.6)")
    parser.add_argument("ply",        nargs="?")
    parser.add_argument("--port",     type=int,   default=8766)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--sor-k",    type=int,   default=20)
    parser.add_argument("--sor-std",  type=float, default=2.0)
    parser.add_argument("--ror-nb",   type=int,   default=5)
    parser.add_argument("--eps",      type=float, default=3.0)
    parser.add_argument("--min-pts",  type=int,   default=10)
    args = parser.parse_args()

    if args.ply:
        ply_path = Path(args.ply)
    else:
        ws = _ROOT / "data" / "workspace"
        auto = sorted(ws.rglob("fused.ply")) if ws.exists() else []
        if auto:
            ply_path = auto[0]; print(f"Авто-найден: {ply_path}")
        else:
            ply_path = _pick_file()

    if not ply_path or not ply_path.exists():
        print("Файл не найден."); sys.exit(1)

    result = run_pipeline(
        ply_path,
        sor_k=args.sor_k, sor_std=args.sor_std,
        ror_min_nb=args.ror_nb,
        eps_factor=args.eps, min_pts=args.min_pts,
    )
    _state.update(result)

    url = f"http://127.0.0.1:{args.port}"
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    print(f"\nОткрой браузер: {url}")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
