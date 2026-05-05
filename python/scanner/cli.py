"""CLI: python -m scanner <command> ..."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import ScanConfig

logger = logging.getLogger(__name__)


# ── Обработчики команд ────────────────────────────────────────────────────────

def _cmd_scan(args: argparse.Namespace) -> int:
    if args.images is None and args.video is None:
        print("Ошибка: укажите --images или --video", file=sys.stderr)
        return 1

    cfg = ScanConfig(
        video_target_frames=args.frames,
        colmap_quality=args.quality,
        target_height_mm=args.height,
        add_base=not args.no_base,
        auto_orient=not args.no_orient,
        remove_ground_plane=args.remove_ground_plane,
    )

    from .pipeline import ScanPipeline

    pipeline = ScanPipeline(cfg)
    input_path = Path(args.video or args.images)
    output_path = Path(args.output)

    def _progress(step: str, progress: float) -> None:
        bar_len = 30
        filled = int(bar_len * progress)
        bar = "#" * filled + "-" * (bar_len - filled)
        print(f"\r[{bar}] {progress*100:5.1f}%  {step:<20}", end="", flush=True)

    try:
        result = pipeline.scan(input_path, output_path, progress_callback=_progress)
    except Exception as exc:
        print(f"\nОшибка: {exc}", file=sys.stderr)
        logger.exception("scan failed")
        return 1

    print()  # newline after progress bar
    print(f"OK  {result.output_path}")
    print(f"    изображений : {result.n_images}")
    print(f"    matcher     : {result.matcher_used}")
    print(f"    время       : {result.elapsed_seconds:.1f} с")
    if result.export:
        e = result.export
        print(f"    watertight  : {e.is_watertight}")
        print(f"    объём       : {e.volume_mm3:.1f} мм³")
        print(f"    bbox        : {e.bbox_mm[0]:.1f} × {e.bbox_mm[1]:.1f} × {e.bbox_mm[2]:.1f} мм")
        if e.warnings:
            for w in e.warnings:
                print(f"    [!] {w}")
    return 0


def _cmd_extract_frames(args: argparse.Namespace) -> int:
    from .config import VideoConfig
    from .video_extractor import VideoFrameExtractor

    cfg = VideoConfig(
        target_frames=args.frames,
        min_frames=args.min_frames,
        max_frames=args.max_frames,
        blur_threshold=args.blur,
        sample_every_n=args.every,
    )
    try:
        result = VideoFrameExtractor().extract(
            Path(args.video), Path(args.output), cfg
        )
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    print(f"Сохранено: {result.count} кадров → {args.output}")
    print(f"Статистика: всего={result.total_frames}"
          f"  выборка={result.sampled_frames}"
          f"  резкость={result.passed_sharpness}"
          f"  уникальных={result.passed_uniqueness}")
    if result.thinned:
        print(f"Прорежено до {args.max_frames} кадров")
    if result.retried:
        print("Повторный проход с ослабленными порогами")
    return 0


def _cmd_process_cloud(args: argparse.Namespace) -> int:
    import time, logging as _logging
    cfg = ScanConfig(
        target_height_mm=args.height,
        add_base=not args.no_base,
        auto_orient=not args.no_orient,
    )
    from .exporter import Exporter
    from .mesh_processor import MeshProcessor

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = Path(args.output)
    ws = out_path.parent / f"workspace_{ts}"
    ws.mkdir(parents=True, exist_ok=True)

    # Лог в файл рядом с STL
    log_file = out_path.parent / f"process_cloud_{ts}.log"
    fh = _logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(_logging.DEBUG)
    fh.setFormatter(_logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt="%H:%M:%S"))
    _logging.getLogger().addHandler(fh)

    try:
        proc = MeshProcessor(cfg)
        repaired = proc.process_cloud(Path(args.input), ws)
        exp = Exporter(cfg)
        result = exp.prepare_and_export(repaired, out_path)
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        logger.exception("process-cloud failed")
        return 1

    print(f"OK  {result.output_path}")
    print(f"    watertight: {result.is_watertight}")
    print(f"    объём:      {result.volume_mm3:.1f} mm3")
    print(f"    workspace:  {ws}")
    print(f"    log:        {log_file}")
    return 0


def _cmd_diagnose(args: argparse.Namespace) -> int:
    from .colmap_diagnostics import diagnose_images, estimate_time

    images_dir = Path(args.images)
    info = diagnose_images(images_dir)
    if not info:
        return 1
    quality = args.quality
    estimate_time(info["n_images"], max(info["avg_w"], info["avg_h"]), quality)
    return 0


def _cmd_resize(args: argparse.Namespace) -> int:
    from .colmap_diagnostics import resize_images

    try:
        resize_images(Path(args.images), Path(args.output), max_size=args.max_size)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError:
        print("Ошибка: uvicorn не установлен (pip install uvicorn)", file=sys.stderr)
        return 1
    uvicorn.run("api.server:app", host=args.host, port=args.port, reload=False)
    return 0


# ── Парсер ────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scanner",
        description="Scanner -- automated 3D scanning system",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # ── scan ──────────────────────────────────────────────────────────────────
    p_scan = sub.add_parser("scan", help="Full pipeline: photos/video -> STL")
    src = p_scan.add_mutually_exclusive_group()
    src.add_argument("--images", metavar="DIR",  help="Directory with photos")
    src.add_argument("--video",  metavar="FILE", help="Video file (.mp4/.mov/.avi)")
    p_scan.add_argument("--output", "-o", required=True, metavar="FILE",
                        help="Output file (.stl / .ply / .obj)")
    p_scan.add_argument("--frames", type=int, default=300, metavar="N",
                        help="Target frame count from video (default: 300)")
    p_scan.add_argument("--quality", choices=["low", "medium", "high"], default="low",
                        help="COLMAP quality: low=5min, medium=30min, high=2h (default: low)")
    p_scan.add_argument("--height", type=float, default=100.0, metavar="MM",
                        help="Target model height in mm (default: 100)")
    p_scan.add_argument("--no-base",            action="store_true", help="Skip flat base")
    p_scan.add_argument("--no-orient",          action="store_true", help="Skip auto-orient")
    p_scan.add_argument("--remove-ground-plane", action="store_true",
                        help="RANSAC: remove table/floor plane before DBSCAN")

    # ── extract-frames ────────────────────────────────────────────────────────
    p_ef = sub.add_parser("extract-frames", help="Step 0: smart frame extraction")
    p_ef.add_argument("video", metavar="VIDEO", help="Path to video file")
    p_ef.add_argument("--output", "-o", required=True, metavar="DIR", help="Output directory")
    p_ef.add_argument("--frames",     type=int,   default=300,   help="Target frame count")
    p_ef.add_argument("--min-frames", type=int,   default=50,    help="Minimum frames")
    p_ef.add_argument("--max-frames", type=int,   default=800,   help="Maximum frames")
    p_ef.add_argument("--blur",       type=float, default=100.0, help="Sharpness threshold")
    p_ef.add_argument("--every",      type=int,   default=3,     help="Sample every Nth frame")

    # ── process-cloud ─────────────────────────────────────────────────────────
    p_pc = sub.add_parser("process-cloud", help="Point cloud PLY -> STL (no COLMAP)")
    p_pc.add_argument("--input",  "-i", required=True, metavar="PLY", help="fused.ply path")
    p_pc.add_argument("--output", "-o", required=True, metavar="FILE", help="Output STL")
    p_pc.add_argument("--height",    type=float, default=100.0, metavar="MM")
    p_pc.add_argument("--no-base",   action="store_true")
    p_pc.add_argument("--no-orient", action="store_true")

    # ── diagnose ──────────────────────────────────────────────────────────────
    p_diag = sub.add_parser("diagnose",
                            help="Check image resolution and estimate COLMAP time")
    p_diag.add_argument("--images", "-i", required=True, metavar="DIR",
                        help="Directory with photos")
    p_diag.add_argument("--quality", choices=["low", "medium", "high"], default="low",
                        help="Quality preset for time estimate (default: low)")

    # ── resize ────────────────────────────────────────────────────────────────
    p_rsz = sub.add_parser("resize",
                           help="Resize images to max_size (preserves EXIF focal length)")
    p_rsz.add_argument("--images",   "-i", required=True, metavar="DIR",
                       help="Source directory with photos")
    p_rsz.add_argument("--output",   "-o", required=True, metavar="DIR",
                       help="Output directory for resized photos")
    p_rsz.add_argument("--max-size", type=int, default=1600, metavar="PX",
                       help="Max pixels on long side (default: 1600)")

    # ── serve ─────────────────────────────────────────────────────────────────
    p_srv = sub.add_parser("serve", help="FastAPI web server")
    p_srv.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    p_srv.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")

    return parser


# ── Точка входа ───────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "scan":           _cmd_scan,
        "extract-frames": _cmd_extract_frames,
        "process-cloud":  _cmd_process_cloud,
        "diagnose":       _cmd_diagnose,
        "resize":         _cmd_resize,
        "serve":          _cmd_serve,
    }

    rc = handlers[args.command](args)
    sys.exit(rc)


# Совместимость со старым entry_point "scanner.cli:app"
app = main


if __name__ == "__main__":
    main()
