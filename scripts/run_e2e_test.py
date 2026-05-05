"""
End-to-end test runner: photos -> STL
Usage:
    python scripts/run_e2e_test.py tst3
    python scripts/run_e2e_test.py tst2
    python scripts/run_e2e_test.py tst1
    python scripts/run_e2e_test.py all
"""
from __future__ import annotations

import io
import logging
import sys
import time
from pathlib import Path

# Force UTF-8 on Windows console to avoid encoding errors in Russian log strings
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"

sys.path.insert(0, str(PYTHON_DIR))

# ── Logging: file + console ────────────────────────────────────────────────────

LOG_DIR = PROJECT_ROOT / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(test_name: str) -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"e2e_{test_name}_{ts}.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

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
    log_file = setup_logging(test_name)
    logger = logging.getLogger("e2e")

    images_dir = PROJECT_ROOT / "data" / "test_images" / test_name
    output_path = PROJECT_ROOT / "data" / "results" / f"{test_name}_output.stl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("E2E test: %s", test_name)
    logger.info("  images: %s", images_dir)
    logger.info("  output: %s", output_path)
    logger.info("  log:    %s", log_file)
    logger.info("=" * 60)

    if not images_dir.exists():
        logger.error("Images directory not found: %s", images_dir)
        return False

    n_images = sum(1 for f in images_dir.iterdir()
                   if f.is_file() and f.suffix.lower() in
                   {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"})
    logger.info("Found %d images", n_images)

    from scanner.config import ScanConfig
    from scanner.pipeline import ScanPipeline

    cfg = ScanConfig(
        colmap_quality=_QUALITY,
        target_height_mm=100.0,
        add_base=True,
        auto_orient=True,
        remove_ground_plane=_REMOVE_GROUND_PLANE,
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
        result = pipeline.scan(images_dir, output_path,
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
    logger.info("  elapsed:  %.1f s", elapsed)
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


_QUALITY = "medium"           # changed via --quality
_REMOVE_GROUND_PLANE = False  # changed via --remove-ground-plane


def main() -> None:
    global _QUALITY, _REMOVE_GROUND_PLANE
    tests = ["tst5", "tst4", "tst3", "tst2", "tst1"]

    args = sys.argv[1:]
    # parse --quality low/medium/high
    if "--quality" in args:
        qi = args.index("--quality")
        _QUALITY = args[qi + 1]
        args = args[:qi] + args[qi + 2:]
    # parse --remove-ground-plane
    if "--remove-ground-plane" in args:
        _REMOVE_GROUND_PLANE = True
        args = [a for a in args if a != "--remove-ground-plane"]

    arg = args[0] if args else "tst3"

    if arg == "all":
        to_run = tests
    elif arg in tests:
        to_run = [arg]
    else:
        print(f"Unknown: {arg!r}. Usage: run_e2e_test.py [--quality low|medium|high] "
              f"[--remove-ground-plane] tst2|tst3|tst1|tst5|all")
        sys.exit(1)

    results: dict[str, bool] = {}
    for name in to_run:
        ok = run_test(name)
        results[name] = ok
        # brief pause between tests
        if name != to_run[-1]:
            time.sleep(2)

    print("\n--- Summary ---")
    for name, ok in results.items():
        print(f"  {name}: {'OK' if ok else 'FAILED'}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
