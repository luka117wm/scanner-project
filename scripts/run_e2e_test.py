"""
End-to-end test runner: photos/video -> STL
Usage:
    python scripts/run_e2e_test.py tst4
    python scripts/run_e2e_test.py tst1_video
    python scripts/run_e2e_test.py all
    python scripts/run_e2e_test.py --quality low all
"""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

# Force UTF-8 on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))

# ── Конфигурация тестов ────────────────────────────────────────────────────────

# Каждый тест: (input_path, is_video, remove_ground_plane)
TEST_CONFIGS: dict[str, tuple[Path, bool, bool]] = {
    "tst1_video": (
        PROJECT_ROOT / "data" / "test_videos" / "tst1.mp4",
        True, False,
    ),
    "tst2": (PROJECT_ROOT / "data" / "test_images" / "tst2", False, False),
    "tst3": (PROJECT_ROOT / "data" / "test_images" / "tst3", False, False),
    "tst4": (PROJECT_ROOT / "data" / "test_images" / "tst4", False, True),
    "tst5": (PROJECT_ROOT / "data" / "test_images" / "tst5", False, False),
    "tst6": (PROJECT_ROOT / "data" / "test_images" / "tst6", False, False),
    "tst7": (PROJECT_ROOT / "data" / "test_images" / "tst7", False, False),
}

# ── Logging ────────────────────────────────────────────────────────────────────

LOG_DIR = PROJECT_ROOT / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(test_name: str) -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"e2e_{test_name}_{ts}.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # Удалить старые хэндлеры от предыдущих тестов
    for h in root.handlers[:]:
        root.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                            datefmt="%H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    return log_file


# ── Test runner ────────────────────────────────────────────────────────────────

def run_test(test_name: str) -> bool:
    if test_name not in TEST_CONFIGS:
        print(f"Unknown test: {test_name!r}")
        return False

    input_path, is_video, remove_gp = TEST_CONFIGS[test_name]
    # --remove-ground-plane флаг переопределяет конфиг теста
    if _REMOVE_GROUND_PLANE:
        remove_gp = True

    output_path = PROJECT_ROOT / "data" / "results" / f"{test_name}_output.stl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    log_file = setup_logging(test_name)
    logger = logging.getLogger("e2e")

    logger.info("=" * 60)
    logger.info("E2E test: %s  [%s]", test_name, "video" if is_video else "images")
    logger.info("  input:  %s", input_path)
    logger.info("  output: %s", output_path)
    logger.info("  quality: %s  remove_gp: %s", _QUALITY, remove_gp)
    logger.info("  log:    %s", log_file)
    logger.info("=" * 60)

    if not input_path.exists():
        logger.error("Input not found: %s", input_path)
        return False

    if not is_video:
        n = sum(1 for f in input_path.iterdir()
                if f.is_file() and f.suffix.lower() in
                {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"})
        logger.info("Found %d images", n)

    from scanner.config import ScanConfig
    from scanner.pipeline import ScanPipeline

    cfg = ScanConfig(
        colmap_quality=_QUALITY,
        target_height_mm=100.0,
        add_base=True,
        auto_orient=True,
        remove_ground_plane=remove_gp,
    )

    pipeline = ScanPipeline(cfg)
    last_step = ""

    def on_progress(step: str, progress: float) -> None:
        nonlocal last_step
        if step != last_step:
            logger.info(">>> STEP: %s  (%.0f%%)", step, progress * 100)
            last_step = step

    t0 = time.monotonic()
    try:
        result = pipeline.scan(input_path, output_path,
                               progress_callback=on_progress)
    except Exception:
        logger.exception("Pipeline FAILED")
        return False

    elapsed = time.monotonic() - t0

    logger.info("=" * 60)
    logger.info("RESULT: %s", "OK" if result.ok else "FAILED (file missing)")
    logger.info("  output:   %s", result.output_path)
    logger.info("  images:   %d", result.n_images)
    logger.info("  matcher:  %s", result.matcher_used)
    logger.info("  elapsed:  %.1f s (%.1f min)", elapsed, elapsed / 60)
    if result.export:
        e = result.export
        logger.info("  watertight:  %s", e.is_watertight)
        logger.info("  open_edges:  %d", e.open_edges)
        logger.info("  printable:   %s", e.is_printable)
        logger.info("  volume:      %.1f mm3", e.volume_mm3)
        logger.info("  bbox:        %.1f x %.1f x %.1f mm",
                    e.bbox_mm[0], e.bbox_mm[1], e.bbox_mm[2])
        if e.warnings:
            for w in e.warnings:
                logger.warning("  [!] %s", w)
    logger.info("  log file: %s", log_file)
    logger.info("=" * 60)

    return result.ok


# ── Entry point ────────────────────────────────────────────────────────────────

_QUALITY = "low"
_REMOVE_GROUND_PLANE = False

VALID = sorted(TEST_CONFIGS.keys())


def main() -> None:
    global _QUALITY, _REMOVE_GROUND_PLANE

    args = sys.argv[1:]

    if "--quality" in args:
        qi = args.index("--quality")
        _QUALITY = args[qi + 1]
        args = args[:qi] + args[qi + 2:]

    if "--remove-ground-plane" in args:
        _REMOVE_GROUND_PLANE = True
        args = [a for a in args if a != "--remove-ground-plane"]

    arg = args[0] if args else "tst5"

    if arg == "all":
        to_run = VALID
    elif arg in TEST_CONFIGS:
        to_run = [arg]
    else:
        print(f"Unknown: {arg!r}")
        print(f"Usage: run_e2e_test.py [--quality low|medium|high] "
              f"[--remove-ground-plane] {'|'.join(VALID)}|all")
        sys.exit(1)

    results: dict[str, bool] = {}
    for name in to_run:
        ok = run_test(name)
        results[name] = ok
        if name != to_run[-1]:
            time.sleep(2)

    print("\n--- Summary ---")
    for name, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"  {name}: {status}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
