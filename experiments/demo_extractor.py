"""
Демо: VideoFrameExtractor на реальном (или синтетическом) видео.

Запуск:
    D:\\3ds\\scanner-project\\venv\\Scripts\\python.exe experiments\\demo_extractor.py

Выход:
    experiments/results/sharpness_hist.png
    experiments/results/mse_hist.png
    experiments/results/pipeline_funnel.png
    experiments/results/timeline.png
"""
from __future__ import annotations

import sys
from pathlib import Path

# Импорты до sys.path — scanner установлен в venv через pip install -e
import cv2
import matplotlib
matplotlib.use("Agg")          # без GUI — работает в любой среде Windows
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from scanner.config import ExtractResult, VideoConfig
from scanner.video_extractor import VideoFrameExtractor, _mse, _sharpness

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
VIDEOS_DIR  = ROOT / "data" / "test_videos"
RESULTS_DIR = ROOT / "experiments" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Конфигурация экстрактора
# ---------------------------------------------------------------------------
CFG = VideoConfig(
    target_frames=300,
    min_frames=50,
    max_frames=800,
    blur_threshold=100.0,
    min_difference=0.03,
    max_difference=0.50,
    sample_every_n=3,
    jpeg_quality=90,
)


# ---------------------------------------------------------------------------
# Шаг 0: выбор / создание видео
# ---------------------------------------------------------------------------
def _find_or_create_video() -> Path:
    """Использует первое .mp4 в test_videos, кроме 'synthetic'.
    Если нет реального — создаёт синтетическое (100 кадров, 20 размытых,
    10 дубликатов) строго по спецификации задачи."""
    candidates = [
        p for p in VIDEOS_DIR.glob("*.mp4")
        if "synthetic" not in p.stem.lower()
    ]
    if candidates:
        video = candidates[0]
        print(f"[video]  используется реальное видео: {video.name}")
        return video

    print("[video]  реальное видео не найдено — создаю синтетическое")
    return _make_synthetic_video(VIDEOS_DIR / "controlled.mp4")


def _make_synthetic_video(path: Path) -> Path:
    """100 кадров с заданной структурой:
      - 20 нормальных  (шум + цвет)
      - 20 размытых    (Gaussian blur, Laplacian var < blur_threshold)
      - 10 дубликатов  (точная копия предыдущего нормального кадра)
      - 50 нормальных  (остаток)
    Итого 100 кадров.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, 30.0, (640, 480))
    assert writer.isOpened(), f"VideoWriter не открылся: {path}"

    rng = np.random.default_rng(0)

    def _normal(i: int) -> np.ndarray:
        base = np.full((480, 640, 3), [
            min(255, i * 5),
            max(0, 200 - i * 2),
            100,
        ], dtype=np.uint8)
        noise = rng.integers(0, 50, (480, 640, 3), dtype=np.uint8)
        return np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    frame_counter = 0
    last_normal: np.ndarray | None = None

    # 20 нормальных
    for i in range(20):
        f = _normal(frame_counter)
        writer.write(f)
        last_normal = f
        frame_counter += 1

    # 20 размытых (сильный Gaussian blur — Laplacian < 10)
    for i in range(20):
        f = _normal(frame_counter)
        f = cv2.GaussianBlur(f, (51, 51), 30)   # sigmaX=30 → очень мягкий
        writer.write(f)
        frame_counter += 1

    # 10 дубликатов (точная копия last_normal)
    assert last_normal is not None
    for _ in range(10):
        writer.write(last_normal.copy())
        frame_counter += 1

    # 50 нормальных
    for i in range(50):
        writer.write(_normal(frame_counter))
        frame_counter += 1

    writer.release()
    print(f"[video]  синтетическое видео создано: {path.name}  ({frame_counter} кадров)")
    return path


# ---------------------------------------------------------------------------
# Шаг 1: сбор метрик по всему видео (одним проходом)
# ---------------------------------------------------------------------------
def collect_metrics(video_path: Path, cfg: VideoConfig) -> dict:
    """Проходит по каждому sample_every_n кадру и собирает:
    - sharpness для всех проверенных кадров
    - MSE между последовательными проверенными кадрами
    - frame_index оригинальный
    """
    cap = cv2.VideoCapture(str(video_path))
    assert cap.isOpened()

    CMP = (320, 180)
    sharpness_vals: list[float] = []
    mse_vals:       list[float] = []      # между соседними sampled кадрами
    frame_indices:  list[int]   = []

    prev_small: np.ndarray | None = None
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % cfg.sample_every_n == 0:
            sharpness_vals.append(_sharpness(frame))
            frame_indices.append(idx)
            small = cv2.resize(frame, CMP)
            if prev_small is not None:
                mse_vals.append(_mse(prev_small, small))
            prev_small = small
        idx += 1

    cap.release()
    return {
        "sharpness":    np.array(sharpness_vals),
        "mse":          np.array(mse_vals),
        "frame_indices": np.array(frame_indices),
        "total_frames": idx,
    }


# ---------------------------------------------------------------------------
# Шаг 2: запуск экстрактора
# ---------------------------------------------------------------------------
def run_extractor(video_path: Path, cfg: VideoConfig) -> ExtractResult:
    out_dir = ROOT / "data" / "results" / "demo_frames"
    print(f"\n[extract] запуск VideoFrameExtractor -> {out_dir}")
    result = VideoFrameExtractor().extract(video_path, out_dir, cfg)
    return result


# ---------------------------------------------------------------------------
# Шаг 3: вывод ExtractResult
# ---------------------------------------------------------------------------
def print_result(result: ExtractResult, video_name: str) -> None:
    print("\n" + "=" * 56)
    print(f"  ExtractResult  [{video_name}]")
    print("=" * 56)
    print(f"  total_frames      = {result.total_frames}")
    print(f"  sampled_frames    = {result.sampled_frames}   (every {CFG.sample_every_n})")
    print(f"  passed_sharpness  = {result.passed_sharpness}"
          f"  ({result.passed_sharpness/max(result.sampled_frames,1)*100:.1f}%)")
    print(f"  passed_uniqueness = {result.passed_uniqueness}"
          f"  ({result.passed_uniqueness/max(result.passed_sharpness,1)*100:.1f}% of sharp)")
    print(f"  saved (count)     = {result.count}")
    print(f"  thinned           = {result.thinned}")
    print(f"  retried           = {result.retried}")
    print(f"  paths[0]          = {result.paths[0] if result.paths else 'N/A'}")
    print("=" * 56)


# ---------------------------------------------------------------------------
# Шаг 4: гистограммы
# ---------------------------------------------------------------------------
PALETTE = {
    "accepted": "#4CAF50",
    "blurry":   "#F44336",
    "too_sim":  "#FF9800",
    "too_diff": "#9C27B0",
    "neutral":  "#90A4AE",
    "thresh":   "#212121",
}

def _save(fig: plt.Figure, name: str) -> Path:
    out = RESULTS_DIR / name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot]   saved -> {out.relative_to(ROOT)}")
    return out


def plot_sharpness(metrics: dict, cfg: VideoConfig) -> None:
    vals  = metrics["sharpness"]
    thr   = cfg.blur_threshold
    n_blur  = int((vals < thr).sum())
    n_sharp = int((vals >= thr).sum())

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(vals[vals < thr],  bins=40, color=PALETTE["blurry"],   alpha=0.85,
            label=f"Blurry  ({n_blur})")
    ax.hist(vals[vals >= thr], bins=60, color=PALETTE["accepted"], alpha=0.85,
            label=f"Sharp   ({n_sharp})")
    ax.axvline(thr, color=PALETTE["thresh"], lw=2, ls="--",
               label=f"blur_threshold = {thr:.0f}")

    ax.set_xlabel("Laplacian variance (sharpness)", fontsize=11)
    ax.set_ylabel("Frame count", fontsize=11)
    ax.set_title("Sharpness distribution of sampled frames", fontsize=12)
    ax.set_xscale("symlog", linthresh=10)
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.4)
    _save(fig, "sharpness_hist.png")


def plot_mse(metrics: dict, cfg: VideoConfig) -> None:
    vals   = metrics["mse"]
    lo, hi = cfg.min_difference, cfg.max_difference

    too_sim  = int((vals <= lo).sum())
    accepted = int(((vals > lo) & (vals < hi)).sum())
    too_diff = int((vals >= hi).sum())

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(vals[vals <= lo],
            bins=30, color=PALETTE["too_sim"],  alpha=0.85,
            label=f"Too similar   (<= {lo})  n={too_sim}")
    ax.hist(vals[(vals > lo) & (vals < hi)],
            bins=50, color=PALETTE["accepted"], alpha=0.85,
            label=f"Accepted zone           n={accepted}")
    ax.hist(vals[vals >= hi],
            bins=30, color=PALETTE["too_diff"], alpha=0.85,
            label=f"Too different (>= {hi})  n={too_diff}")
    ax.axvline(lo, color=PALETTE["thresh"], lw=2, ls="--",
               label=f"min_difference = {lo}")
    ax.axvline(hi, color=PALETTE["thresh"], lw=2, ls=":",
               label=f"max_difference = {hi}")

    ax.set_xlabel("Normalised MSE  (0 = identical, 1 = max difference)", fontsize=11)
    ax.set_ylabel("Frame pair count", fontsize=11)
    ax.set_title("Frame-to-frame MSE distribution", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.4)
    _save(fig, "mse_hist.png")


def plot_funnel(result: ExtractResult) -> None:
    stages  = ["Total\nframes", "Sampled\n(every N)", "Passed\nsharpness",
               "Passed\nuniqueness", "Saved"]
    values  = [result.total_frames, result.sampled_frames,
               result.passed_sharpness, result.passed_uniqueness,
               result.count]
    colors  = [PALETTE["neutral"], PALETTE["neutral"], PALETTE["accepted"],
               PALETTE["accepted"], "#1565C0"]

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(stages, values, color=colors, edgecolor="white", linewidth=0.8)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + values[0] * 0.01,
                str(val), ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("Frame count", fontsize=11)
    ax.set_title("Extraction pipeline funnel", fontsize=12)
    ax.set_ylim(0, values[0] * 1.12)
    ax.grid(axis="y", alpha=0.4)
    _save(fig, "pipeline_funnel.png")


def plot_timeline(metrics: dict, cfg: VideoConfig) -> None:
    """Шарпнесс каждого проверенного кадра во времени."""
    indices    = metrics["frame_indices"]
    sharpness  = metrics["sharpness"]
    fps        = 30.0
    times      = indices / fps          # секунды
    thr        = cfg.blur_threshold

    sharp_mask = sharpness >= thr
    blur_mask  = ~sharp_mask

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(times[sharp_mask], sharpness[sharp_mask],
               s=4, alpha=0.5, color=PALETTE["accepted"], label="Sharp")
    ax.scatter(times[blur_mask],  sharpness[blur_mask],
               s=4, alpha=0.5, color=PALETTE["blurry"],   label="Blurry")
    ax.axhline(thr, color=PALETTE["thresh"], lw=1.5, ls="--",
               label=f"blur_threshold = {thr:.0f}")

    ax.set_xlabel("Time in video (seconds)", fontsize=11)
    ax.set_ylabel("Laplacian variance", fontsize=11)
    ax.set_title("Sharpness over time (sampled frames)", fontsize=12)
    ax.set_yscale("symlog", linthresh=10)
    ax.legend(fontsize=10, markerscale=3)
    ax.grid(alpha=0.3)
    _save(fig, "timeline.png")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> None:
    video = _find_or_create_video()

    print("\n[metrics] сбор sharpness и MSE по всему видео...")
    metrics = collect_metrics(video, CFG)
    print(f"[metrics] sampled={len(metrics['sharpness'])}  mse_pairs={len(metrics['mse'])}")

    result = run_extractor(video, CFG)
    print_result(result, video.name)

    print("\n[plots]  генерация гистограмм...")
    plot_sharpness(metrics, CFG)
    plot_mse(metrics, CFG)
    plot_funnel(result)
    plot_timeline(metrics, CFG)
    print(f"\n[done]   все графики -> {RESULTS_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
