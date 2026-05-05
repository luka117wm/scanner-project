"""Шаги 9-10: PrintPreparation (C++) + экспорт STL/PLY/OBJ."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from .config import ScanConfig

logger = logging.getLogger(__name__)

_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@dataclass
class ExportResult:
    output_path: Path
    is_watertight: bool
    is_printable: bool
    open_edges: int
    volume_mm3: float
    surface_area_mm2: float
    bbox_mm: tuple[float, float, float]
    warnings: list[str]


class Exporter:
    """
    Шаги 9-10 пайплайна:
      9 — auto_orient, (опционально) cut + add_flat_base, scale_to_size
      10 — save_stl / save_ply / save_obj
    """

    def __init__(self, config: ScanConfig) -> None:
        self.config = config

    def prepare_and_export(self, mesh_ply: Path, output_path: Path) -> ExportResult:
        """
        Загрузить PLY, подготовить к печати, экспортировать в output_path.
        Формат определяется по суффиксу output_path (.stl / .ply / .obj).
        """
        from scanner import PrintPreparation, TriangleMesh

        mesh = TriangleMesh()
        if not mesh.load_ply(str(mesh_ply)):
            raise RuntimeError(f"Не удалось загрузить меш: {mesh_ply}")

        logger.info("Шаг 9: подготовка к печати (%d вершин, %d граней)",
                    mesh.num_vertices(), mesh.num_faces())

        pp = PrintPreparation(mesh)

        # ── Шаг 9a: авто-ориентация ──────────────────────────────────────────
        if self.config.auto_orient:
            pp.auto_orient()
            logger.info("  auto_orient: выполнена")

        # ── Шаг 9b: масштаб (до основания — чтобы base_cut/thickness были в мм) ──
        pp.scale_to_size(self.config.target_height_mm, "z")
        bb = mesh.bounding_box()
        actual_h = float(bb.max[2] - bb.min[2])
        logger.info("  scale_to_size: %.1f мм по Z (фактически %.2f мм)",
                    self.config.target_height_mm, actual_h)

        # ── Шаг 9c: плоское основание ─────────────────────────────────────────
        if self.config.add_base:
            self._add_base(pp, mesh)

        # ── Шаг 9d: отчёт о печатабельности ──────────────────────────────────
        rpt = pp.check_printability()
        if rpt.warnings:
            for w in rpt.warnings:
                logger.warning("  Предупреждение: %s", w)

        # ── Шаг 10: экспорт ───────────────────────────────────────────────────
        output_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = output_path.suffix.lower()

        ok = False
        if suffix == ".stl":
            ok = mesh.save_stl(str(output_path))
        elif suffix == ".ply":
            ok = mesh.save_ply(str(output_path))
        elif suffix == ".obj":
            ok = mesh.save_obj(str(output_path))
        else:
            raise ValueError(
                f"Неизвестный формат экспорта: {suffix!r} "
                f"(поддерживается: .stl .ply .obj)"
            )

        if not ok:
            raise RuntimeError(f"Ошибка записи файла: {output_path}")

        bb_final = mesh.bounding_box()
        logger.info("Шаг 10: экспорт → %s (%.1f KB)",
                    output_path.name, output_path.stat().st_size / 1024)

        return ExportResult(
            output_path=output_path,
            is_watertight=rpt.is_watertight,
            is_printable=rpt.is_printable(),
            open_edges=rpt.open_edges,
            volume_mm3=rpt.volume_mm3,
            surface_area_mm2=rpt.surface_area_mm2,
            bbox_mm=(
                float(bb_final.max[0] - bb_final.min[0]),
                float(bb_final.max[1] - bb_final.min[1]),
                float(bb_final.max[2] - bb_final.min[2]),
            ),
            warnings=list(rpt.warnings),
        )

    # ── Вспомогательные методы ─────────────────────────────────────────────────

    def _add_base(self, pp, mesh) -> None:
        """
        Добавляет основание. scale_to_size уже выполнен — все размеры в мм.
        Если меш watertight — срезаем 2мм снизу (плоское дно) + диск-подставка.
        Если есть дыры — закрываем add_flat_base.
        """
        bb = mesh.bounding_box()
        z_height = float(bb.max[2] - bb.min[2])
        if z_height < 1e-6:
            logger.warning("  add_base: нулевая высота меша, пропускаем")
            return

        open_edges = len(mesh.find_boundary_edges())
        if open_edges > 0:
            # Меш не watertight — закрываем дыры стенками
            pp.add_flat_base(thickness=self.config.base_thickness_mm)
            logger.info("  add_flat_base: %d открытых рёбер", open_edges)
        else:
            # Срез снизу создаёт плоское дно — диск прилегает без зазора
            cut_depth = self.config.base_cut_depth_mm
            if cut_depth > 0 and cut_depth < z_height * 0.1:
                z_cut = float(bb.min[2]) + cut_depth
                cx = float((bb.min[0] + bb.max[0]) * 0.5)
                cy = float((bb.min[1] + bb.max[1]) * 0.5)
                pp.cut_with_plane([cx, cy, z_cut], [0.0, 0.0, -1.0])
                logger.info("  cut_with_plane: дно срезано на %.1f мм", cut_depth)
                # После среза проверяем снова — если дыры появились, flat_base
                open_after = len(mesh.find_boundary_edges())
                if open_after > 0:
                    pp.add_flat_base(thickness=self.config.base_thickness_mm)
                    logger.info("  add_flat_base после среза: %d рёбер", open_after)
                    return
            pp.add_disc_stand(
                radius_fraction=self.config.stand_radius_fraction,
                thickness=self.config.base_thickness_mm,
            )
            logger.info("  add_disc_stand: r=%.0f%% t=%.1f мм",
                        self.config.stand_radius_fraction * 100,
                        self.config.base_thickness_mm)
