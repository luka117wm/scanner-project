"""Главный пайплайн: вход (фото/видео) → STL."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .config import ScanConfig
from .colmap_runner import ColmapRunner
from .exporter import ExportResult, Exporter
from .mesh_processor import MeshProcessor

logger = logging.getLogger(__name__)

_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

# Названия шагов и их «вес» в общем прогрессе
_STEPS: list[tuple[str, float]] = [
    ("extract_frames",  0.05),   # шаг 0
    ("colmap",          0.30),   # шаг 1
    ("point_cloud",     0.15),   # шаги 2-4
    ("poisson",         0.15),   # шаг 5
    ("mesh_repair",     0.10),   # шаги 6-8
    ("print_prep",      0.05),   # шаг 9
    ("export",          0.05),   # шаг 10
]

ProgressCallback = Callable[[str, float], None]


# ── Результат ─────────────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    output_path:     Path
    workspace:       Path
    n_images:        int
    matcher_used:    str
    elapsed_seconds: float
    steps_completed: list[str] = field(default_factory=list)
    export:          ExportResult | None = None

    @property
    def ok(self) -> bool:
        return self.output_path.exists()


# ── Пайплайн ──────────────────────────────────────────────────────────────────

class ScanPipeline:
    """
    Оркестратор полного пайплайна 3D-сканирования:
      0  — извлечение кадров из видео (если нужно)
      1  — COLMAP (feature_extractor → matcher → mapper → dense → fusion)
      2-4 — PointCloud (SOR, DBSCAN, downsample, normals)
      5  — Poisson meshing (Open3D)
      6-8 — MeshRepair (C++)
      9  — PrintPreparation (C++)
      10 — Export STL/PLY/OBJ
    """

    def __init__(self, config: ScanConfig | None = None) -> None:
        self.config = config or ScanConfig()

    def scan(
        self,
        input_path: Path,
        output_path: Path,
        progress_callback: ProgressCallback | None = None,
    ) -> ScanResult:
        """
        Запустить полный пайплайн.

        Args:
            input_path:  папка с фото ИЛИ путь к видео-файлу.
            output_path: путь к итоговому файлу (.stl / .ply / .obj).
            progress_callback: вызывается при начале каждого шага как
                               callback(step_name, progress_0_to_1).
        Returns:
            ScanResult с путём к выходному файлу и метаданными.
        """
        input_path  = input_path.resolve()
        output_path = output_path.resolve()

        input_type = self._detect_input_type(input_path)
        workspace  = self._make_workspace()

        logger.info("=== ScanPipeline start ===")
        logger.info("  input:     %s (%s)", input_path, input_type)
        logger.info("  output:    %s", output_path)
        logger.info("  workspace: %s", workspace)

        t0 = time.monotonic()
        steps_done: list[str] = []
        cumulative = 0.0

        def _progress(step: str) -> None:
            nonlocal cumulative
            weight = dict(_STEPS).get(step, 0.0)
            if progress_callback:
                progress_callback(step, cumulative)
            logger.info("Step: %s (%.0f%%)", step, cumulative * 100)
            cumulative = min(1.0, cumulative + weight)

        # ── Шаг 0: извлечение кадров из видео ────────────────────────────────
        _progress("extract_frames")
        if input_type == "video":
            image_dir = workspace / "frames"
            image_dir = self._extract_frames(input_path, image_dir)
        else:
            image_dir = input_path
        steps_done.append("extract_frames")

        # ── Шаг 1: COLMAP ─────────────────────────────────────────────────────
        _progress("colmap")
        colmap_result = ColmapRunner(self.config).run(
            image_dir=image_dir,
            workspace=workspace / "colmap",
            input_type=input_type,
        )
        steps_done.append("colmap")

        # ── Шаги 2-8: облако → меш ───────────────────────────────────────────
        _progress("point_cloud")
        mesh_proc = MeshProcessor(self.config)
        repaired_ply = mesh_proc.process_cloud(
            ply_path=colmap_result.fused_ply,
            workspace=workspace / "mesh",
        )
        steps_done.append("point_cloud")
        steps_done.append("poisson")
        steps_done.append("mesh_repair")

        _progress("poisson")     # визуальный прогресс — уже выполнено выше
        _progress("mesh_repair")

        # ── Шаги 9-10: подготовка к печати + экспорт ─────────────────────────
        _progress("print_prep")
        exp = Exporter(self.config)
        export_result = exp.prepare_and_export(
            mesh_ply=repaired_ply,
            output_path=output_path,
        )
        steps_done.append("print_prep")

        _progress("export")
        steps_done.append("export")

        if progress_callback:
            progress_callback("done", 1.0)

        elapsed = time.monotonic() - t0
        logger.info("=== ScanPipeline done: %.1f сек → %s ===", elapsed, output_path)

        return ScanResult(
            output_path=output_path,
            workspace=workspace,
            n_images=colmap_result.n_images,
            matcher_used=colmap_result.matcher_used,
            elapsed_seconds=elapsed,
            steps_completed=steps_done,
            export=export_result,
        )

    # ── Вспомогательные методы ────────────────────────────────────────────────

    def _detect_input_type(self, input_path: Path) -> str:
        """Определить тип входа: 'video' или 'photos'."""
        if self.config.input_type != "auto":
            return self.config.input_type
        if input_path.is_file() and input_path.suffix.lower() in _VIDEO_EXTS:
            return "video"
        return "photos"

    def _make_workspace(self) -> Path:
        """Создать уникальную папку workspace с временной меткой."""
        project_root = Path(__file__).resolve().parents[2]
        ts = time.strftime("%Y%m%d_%H%M%S")
        ws = project_root / "data" / "workspace" / ts
        ws.mkdir(parents=True, exist_ok=True)
        return ws

    def _extract_frames(self, video_path: Path, output_dir: Path) -> Path:
        """Шаг 0: VideoFrameExtractor → папка с JPEG."""
        from .config import VideoConfig
        from .video_extractor import VideoFrameExtractor

        cfg = VideoConfig(
            target_frames=self.config.video_target_frames,
            min_frames=self.config.video_min_frames,
            max_frames=self.config.video_max_frames,
            blur_threshold=self.config.video_blur_threshold,
            min_difference=self.config.video_min_difference,
            max_difference=self.config.video_max_difference,
            sample_every_n=self.config.video_sample_every_n,
        )
        result = VideoFrameExtractor().extract(video_path, output_dir, cfg)
        logger.info("  Извлечено %d кадров из видео", result.count)
        return output_dir
