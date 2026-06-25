"""
Эксперимент 1: зависимость качества реконструкции от числа входных изображений.

Запуск:
    python experiments/exp1_image_count.py --images D:\path\to\tst7

Подмножества создаются через hardlink (мгновенно, без дублирования файлов).
Результат каждого прогона сохраняется в experiments/results/exp1/nXXX/metrics.json.
После всех прогонов выводится таблица и сохраняется summary.csv + график.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "python"))

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
SUBSETS     = [20, 40, 80, 120, 200, 222]
RESULTS_DIR = _ROOT / "experiments" / "results" / "exp1_image_count"


# ── Вспомогательные функции ────────────────────────────────────────────────────

def _ply_element_count(ply_path: Path, element: str) -> int | None:
    """Читает количество элементов (vertex/face) из заголовка PLY без загрузки файла."""
    try:
        with open(ply_path, "rb") as f:
            for _ in range(50):
                line = f.readline().decode("ascii", errors="ignore").strip()
                if line == "end_header":
                    break
                if line.startswith(f"element {element}"):
                    return int(line.split()[-1])
    except Exception:
        pass
    return None


def _colmap_registered(workspace: Path) -> int | None:
    """Количество зарегистрированных изображений из COLMAP images.txt."""
    images_txt = workspace / "colmap" / "sparse" / "0" / "images.txt"
    if not images_txt.exists():
        return None
    try:
        with open(images_txt, encoding="utf-8") as f:
            for line in f:
                # Ищем строку: # Number of images: N, ...
                if line.startswith("# Number of images:"):
                    return int(line.split(":")[1].strip().split(",")[0])
        # Fallback: считаем строки с метаданными вручную
        # (формат: 2 строки на изображение, первая имеет >= 9 полей)
        count = 0
        with open(images_txt, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and len(line.split()) >= 9:
                    count += 1
        return count if count else None
    except Exception:
        return None


def _check_watertight(mesh_path: Path) -> bool | None:
    try:
        import trimesh as tm
        m = tm.load(str(mesh_path), force="mesh", process=False)
        return bool(m.is_watertight)
    except Exception:
        return None


def _make_subset(src: Path, n: int, dest: Path) -> None:
    """
    Создаёт папку с N равномерно отобранными изображениями.
    Использует hardlinks (мгновенно, без копирования данных).
    Fallback — shutil.copy2.
    """
    files = sorted(f for f in src.iterdir()
                   if f.is_file() and f.suffix.lower() in _IMAGE_EXTS)
    total = len(files)
    if n >= total:
        indices = list(range(total))
    else:
        indices = list(np.linspace(0, total - 1, n, dtype=int))

    dest.mkdir(parents=True, exist_ok=True)
    for idx in indices:
        f   = files[idx]
        dst = dest / f.name
        if dst.exists():
            continue
        try:
            os.link(f, dst)           # hardlink — мгновенно, без дублирования
        except (OSError, NotImplementedError):
            shutil.copy2(f, dst)      # fallback для FAT / разных томов


# ── Основной прогон ────────────────────────────────────────────────────────────

def run_subset(n: int, src_images: Path, out_dir: Path) -> dict:
    metrics_file = out_dir / "metrics.json"

    if metrics_file.exists():
        print(f"  [skip] n={n}: уже выполнено")
        with open(metrics_file, encoding="utf-8") as f:
            return json.load(f)

    out_dir.mkdir(parents=True, exist_ok=True)
    subset_dir  = out_dir / "images"
    output_path = out_dir / f"result_n{n:03d}.stl"

    print(f"  Подмножество: {n} фото → {subset_dir}")
    _make_subset(src_images, n, subset_dir)

    metrics: dict = {"n_input": n}

    try:
        from scanner.config import ScanConfig
        from scanner.pipeline import ScanPipeline

        cfg = ScanConfig(colmap_quality="medium", poisson_depth=9)

        print(f"  Пайплайн запущен...")
        result = ScanPipeline(cfg).scan(input_path=subset_dir,
                                        output_path=output_path)
        ws = result.workspace

        metrics["elapsed_sec"]  = round(result.elapsed_seconds, 1)
        metrics["n_registered"] = _colmap_registered(ws)

        fused = ws / "colmap" / "dense" / "fused.ply"
        dense = _ply_element_count(fused, "vertex")
        metrics["dense_pts"]   = dense
        metrics["dense_pts_k"] = round(dense / 1000, 1) if dense else None

        clean = ws / "mesh" / "point_cloud_clean.ply"
        pts   = _ply_element_count(clean, "vertex")
        metrics["clean_pts"]   = pts
        metrics["clean_pts_k"] = round(pts / 1000, 1) if pts else None

        mesh_ply = next(
            (ws / "mesh" / name for name in ("mesh_fixed.ply", "mesh_repaired.ply")
             if (ws / "mesh" / name).exists()),
            None,
        )
        if mesh_ply:
            faces = _ply_element_count(mesh_ply, "face")
            metrics["faces"]      = faces
            metrics["faces_k"]    = round(faces / 1000, 1) if faces else None
            metrics["watertight"] = _check_watertight(mesh_ply)
        else:
            metrics["faces"] = metrics["faces_k"] = metrics["watertight"] = None

        metrics["workspace"] = str(ws)
        metrics["error"]     = None

        print(f"  ✓  dense={metrics['dense_pts_k']}K  "
              f"clean={metrics['clean_pts_k']}K  "
              f"faces={metrics['faces_k']}K  "
              f"WT={'Да' if metrics['watertight'] else 'Нет'}  "
              f"t={metrics['elapsed_sec']}s")

    except Exception as exc:
        metrics["error"] = str(exc)
        print(f"  ✗  ОШИБКА: {exc}")

    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    return metrics


# ── Таблица и CSV ──────────────────────────────────────────────────────────────

def print_table(rows: list[dict]) -> None:
    sep = "─" * 74
    print(f"\n{sep}")
    print("Таблица 4.2 – Зависимость метрик реконструкции от числа фотографий")
    print(sep)
    print(f"{'Фото':>5} │{'Зарег.':>7} │{'Dense,тыс':>10} │"
          f"{'Фильтр,тыс':>11} │{'Грани,тыс':>10} │{'WT':>4} │{'Время':>8}")
    print(sep)
    for m in rows:
        if m.get("error"):
            print(f"  {m['n_input']:>3}  │ ОШИБКА: {str(m['error'])[:52]}")
            continue
        reg   = str(m.get("n_registered") or "—")
        dense = str(m.get("dense_pts_k")  or "—")
        clean = str(m.get("clean_pts_k")  or "—")
        faces = str(m.get("faces_k")      or "—")
        wt    = ("Да" if m["watertight"] else "Нет") if m.get("watertight") is not None else "—"
        t     = f"{m['elapsed_sec']:.0f}s" if m.get("elapsed_sec") else "—"
        print(f"  {m['n_input']:>3}  │{reg:>7} │{dense:>10} │"
              f"{clean:>11} │{faces:>10} │{wt:>4} │{t:>8}")
    print(sep)


def save_csv(rows: list[dict], path: Path) -> None:
    fields = ["n_input", "n_registered", "dense_pts_k", "clean_pts_k",
              "faces_k", "watertight", "elapsed_sec", "error"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for m in rows:
            w.writerow({k: m.get(k, "") for k in fields})
    print(f"CSV: {path}")


# ── График ────────────────────────────────────────────────────────────────────

def save_plot(rows: list[dict], path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("matplotlib не установлен — график пропущен")
        return

    ok = [m for m in rows if not m.get("error") and m.get("dense_pts_k")]
    if not ok:
        print("Нет данных для графика")
        return

    x      = [m["n_input"]     for m in ok]
    y_dense = [m["dense_pts_k"] for m in ok]
    y_clean = [m.get("clean_pts_k") for m in ok]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x, y_dense, "o-", linewidth=2, markersize=7,
            color="#2563eb", label="Dense cloud (до фильтрации)")
    if any(v is not None for v in y_clean):
        ax.plot(x, y_clean, "s--", linewidth=1.8, markersize=6,
                color="#16a34a", label="После фильтрации (DBSCAN)")

    ax.set_xlabel("Число фотографий", fontsize=12)
    ax.set_ylabel("Число точек, тыс.", fontsize=12)
    ax.set_title("Рисунок 4.1 – Зависимость плотности облака от числа фотографий",
                 fontsize=11, pad=12)
    ax.set_xticks(SUBSETS)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"График: {path}")
    plt.close(fig)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Эксперимент 1: качество реконструкции vs. число фотографий"
    )
    parser.add_argument("--images",  required=True,
                        help="Папка с исходными фотографиями (tst7, 222 фото)")
    parser.add_argument("--subsets", nargs="+", type=int, default=SUBSETS,
                        help=f"Подмножества (по умолчанию: {SUBSETS})")
    args = parser.parse_args()

    src = Path(args.images).resolve()
    if not src.exists():
        sys.exit(f"Папка не найдена: {src}")

    all_files = sorted(f for f in src.iterdir()
                       if f.suffix.lower() in _IMAGE_EXTS)
    print(f"Источник : {src}")
    print(f"Всего фото: {len(all_files)}")
    print(f"Подмножества: {args.subsets}")
    print(f"Результаты: {RESULTS_DIR}\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_metrics = []
    subsets = [n for n in args.subsets if n <= len(all_files)]
    for i, n in enumerate(subsets, 1):
        print(f"[{i}/{len(subsets)}] n={n}")
        m = run_subset(n, src, RESULTS_DIR / f"n{n:03d}")
        all_metrics.append(m)

    print_table(all_metrics)
    save_csv(all_metrics, RESULTS_DIR / "summary.csv")
    save_plot(all_metrics, RESULTS_DIR / "fig4_1_density_vs_photos.png")


if __name__ == "__main__":
    main()
