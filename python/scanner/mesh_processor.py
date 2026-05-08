"""Шаги 2-8: PointCloud (C++) → Poisson (COLMAP) → MeshRepair (C++)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from .config import ScanConfig

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MeshProcessor:
    """
    Шаги 2-8 пайплайна:
      2 — Statistical Outlier Removal
      2b — Radius Outlier Removal (scatter-шум: трава, одиночные точки)
      3 — DBSCAN (наибольший кластер, adaptive eps)
      4 — Voxel downsample (только >5M точек) + estimate normals
      5 — Poisson meshing (COLMAP poisson_mesher)
      6-8 — MeshRepair (degenerate, merge, manifold, holes, smooth)
    """

    def __init__(self, config: ScanConfig) -> None:
        self.config = config

    def process_cloud(self, ply_path: Path, workspace: Path) -> Path:
        """
        Облако точек → отремонтированный меш.
        Возвращает путь к repaired_mesh.ply в workspace.
        """
        from scanner import MeshRepair, PointCloud, TriangleMesh

        workspace.mkdir(parents=True, exist_ok=True)

        # ── Шаги 2-4: PointCloud ─────────────────────────────────────────────
        pc = PointCloud()
        if not pc.load_ply(str(ply_path)):
            raise RuntimeError(f"Cannot load PLY: {ply_path}")
        logger.info("Step 2-4: cloud %d pts from %s", pc.size(), ply_path.name)

        # Шаг 2: Statistical Outlier Removal
        before = pc.size()
        pc = pc.statistical_outlier_removal(
            k=self.config.outlier_k,
            std_ratio=self.config.outlier_std,
        )
        logger.info("  SOR: %d -> %d pts", before, pc.size())

        # Шаг 2b: Radius Outlier Removal — scatter-шум (трава, листья, одиночки)
        # Пропускаем для разреженных облаков (<500K): маленький eps → удаляет
        # настоящие точки объекта из-за низкой плотности (low quality COLMAP).
        eps = self._estimate_dbscan_eps(pc)
        if pc.size() >= 500_000:
            ror_radius = eps * self.config.ror_radius_factor
            before = pc.size()
            pc = self._radius_outlier_removal(pc, radius=ror_radius,
                                              nb_points=self.config.ror_nb_points)
            logger.info("  ROR: %d -> %d pts (r=%.5f=eps*%.1f, min_nb=%d)",
                        before, pc.size(), ror_radius,
                        self.config.ror_radius_factor, self.config.ror_nb_points)
        else:
            logger.info("  ROR: skipped (sparse cloud %d pts < 500K)", pc.size())

        # Шаг 2c: удалить доминирующую плоскость (стол) перед DBSCAN
        if self.config.remove_ground_plane:
            self._remove_ground_plane(pc)

        # Шаг 3: DBSCAN — наибольший кластер, eps адаптивный
        before = pc.size()
        logger.info("  DBSCAN eps=%.5f (auto), min_pts=%d",
                    eps, self.config.dbscan_min_pts)
        pc = pc.segment_largest_cluster(
            eps=eps,
            min_points=self.config.dbscan_min_pts,
            min_cluster_fraction=self.config.dbscan_min_cluster_fraction,
        )
        logger.info("  DBSCAN: %d -> %d pts (kept %.1f%%, clusters>=%.0f%% of largest)",
                    before, pc.size(), 100.0 * pc.size() / max(before, 1),
                    self.config.dbscan_min_cluster_fraction * 100)

        # Шаг 4: Voxel downsample — только для очень больших облаков (>5M)
        # COLMAP poisson_mesher справляется с 1-3M точек напрямую
        if pc.size() > 5_000_000:
            voxel_size = self._estimate_voxel_size(pc)
            before = pc.size()
            pc = pc.voxel_downsample(voxel_size)
            logger.info("  Voxel: %d -> %d pts (size=%.5f)",
                        before, pc.size(), voxel_size)

        # Estimate normals (нужны для Poisson)
        pc.estimate_normals(k=30)
        logger.info("  Normals estimated (%d pts)", pc.size())

        # Сохранить PLY с нормалями
        clean_ply = workspace / "point_cloud_clean.ply"
        if not pc.save_ply(str(clean_ply)):
            raise RuntimeError(f"Cannot save cloud: {clean_ply}")
        logger.info("  Saved: %s (%d pts)", clean_ply.name, pc.size())

        # ── Шаг 5: Poisson meshing (COLMAP) ──────────────────────────────────
        raw_mesh_ply = workspace / "mesh_raw.ply"
        self._poisson_mesh(clean_ply, raw_mesh_ply)

        # ── Шаги 6-8: MeshRepair (C++) ────────────────────────────────────────
        mesh = TriangleMesh()
        if not mesh.load_ply(str(raw_mesh_ply)):
            raise RuntimeError(f"Cannot load mesh PLY: {raw_mesh_ply}")
        logger.info("Steps 6-8: repair mesh (%d verts, %d faces)",
                    mesh.num_vertices(), mesh.num_faces())

        repair = MeshRepair(mesh)
        report = repair.repair_all(
            smooth_iterations=self.config.smooth_iterations,
            max_hole_edges=self.config.max_hole_edges,
        )
        logger.info(
            "  Repair: degen=%d dup=%d merged=%d manifold=%d holes=%d smooth=%d",
            report.degenerate_removed, report.duplicate_removed,
            report.vertices_merged, report.non_manifold_removed,
            report.holes_filled, report.smooth_iterations,
        )

        repaired_ply = workspace / "mesh_repaired.ply"
        if not mesh.save_ply(str(repaired_ply)):
            raise RuntimeError(f"Cannot save repaired PLY: {repaired_ply}")
        logger.info("  Repaired: %s (%d verts, %d faces)",
                    repaired_ply.name, mesh.num_vertices(), mesh.num_faces())

        # Шаг 8.5: pymeshfix — закрыть оставшиеся дыры
        repaired_ply = self._apply_pymeshfix(repaired_ply, workspace)

        return repaired_ply

    # ── Вспомогательные методы ─────────────────────────────────────────────────

    def _estimate_dbscan_eps(self, pc) -> float:
        """
        Адаптивный eps для DBSCAN — через среднее расстояние между точками.

        Для поверхностного облака точек (COLMAP fused.ply) среднее расстояние
        между соседними точками ≈ diagonal / sqrt(N). Берём 3x этого значения,
        чтобы DBSCAN надёжно соединял соседние точки объекта.

        Это масштабируется автоматически под любые координаты COLMAP.
        """
        bb = pc.bounding_box()
        diag = float(np.linalg.norm(bb.max - bb.min))
        n = pc.size()
        if n < 2 or diag < 1e-9:
            return self.config.dbscan_eps
        # Среднее расстояние на поверхности: площадь bbox / N → spacing
        avg_surface_spacing = diag / max(n ** 0.5, 1.0)
        eps = avg_surface_spacing * self.config.dbscan_eps_factor
        logger.debug("  eps auto: diag=%.4f N=%d spacing=%.5f eps=%.5f",
                     diag, n, avg_surface_spacing, eps)
        return max(eps, 1e-6)

    def _poisson_mesh(self, clean_ply: Path, out_ply: Path) -> None:
        """Шаг 5: Poisson surface reconstruction через COLMAP poisson_mesher."""
        from .colmap_runner import ColmapRunner

        logger.info("Step 5: Poisson (COLMAP depth=%d) <- %s",
                    self.config.poisson_depth, clean_ply.name)
        ColmapRunner(self.config).poisson_mesh(
            clean_ply, out_ply,
            depth=self.config.poisson_depth,
            trim=self.config.poisson_trim,
        )
        logger.info("  Saved: %s", out_ply.name)

    def _apply_pymeshfix(self, ply_path: Path, workspace: Path) -> Path:
        """Шаг 8.5: pymeshfix — закрыть оставшиеся дыры, получить watertight меш."""
        try:
            import pymeshfix
            import trimesh as tm_lib
        except ImportError:
            logger.warning("  pymeshfix/trimesh not installed, skipping")
            return ply_path

        try:
            loaded = tm_lib.load(str(ply_path), force="mesh", process=False)
            if loaded.is_watertight:
                logger.info("  pymeshfix: already watertight, skipping")
                return ply_path

            v = np.asarray(loaded.vertices, dtype=np.float64)
            f = np.asarray(loaded.faces,    dtype=np.int32)

            # pymeshfix API: clean_from_arrays returns (v_out, f_out)
            v_out, f_out = pymeshfix.clean_from_arrays(v, f)

            fixed = tm_lib.Trimesh(vertices=v_out, faces=f_out, process=False)
            fixed_ply = workspace / "mesh_fixed.ply"
            fixed.export(str(fixed_ply))

            logger.info(
                "  pymeshfix: %d→%d verts, %d→%d faces, watertight=%s",
                len(v), len(v_out), len(f), len(f_out), fixed.is_watertight,
            )
            return fixed_ply
        except Exception as exc:
            logger.warning("  pymeshfix failed (%s), using repaired PLY", exc)
            return ply_path

    def _remove_ground_plane(self, pc) -> None:
        """
        RANSAC: находит доминирующую плоскость (стол/пол) и удаляет точки
        на ней и ниже неё. Объект остаётся на «верхней» стороне.
        Модифицирует pc на месте.
        """
        pts = np.asarray(pc.points, dtype=np.float64)
        n = len(pts)
        if n < 100:
            return

        bb_diag = float(np.linalg.norm(pts.max(axis=0) - pts.min(axis=0)))
        threshold = bb_diag * 0.01  # 1% bbox diagonal — допуск плоскости

        best_count = 0
        best_normal: np.ndarray | None = None
        best_point: np.ndarray | None = None
        rng = np.random.default_rng(42)

        for _ in range(500):
            idx = rng.choice(n, 3, replace=False)
            p1, p2, p3 = pts[idx]
            normal = np.cross(p2 - p1, p3 - p1)
            norm_len = float(np.linalg.norm(normal))
            if norm_len < 1e-10:
                continue
            normal /= norm_len
            count = int((np.abs((pts - p1) @ normal) < threshold).sum())
            if count > best_count:
                best_count = count
                best_normal = normal.copy()
                best_point = p1.copy()

        if best_normal is None:
            logger.warning("  Ground plane: RANSAC failed")
            return

        inlier_frac = best_count / n
        if inlier_frac < 0.05:
            logger.info("  Ground plane: no dominant plane (%.1f%% inliers), skip",
                        inlier_frac * 100)
            return

        # Знаковое расстояние: + над плоскостью, − под
        signed = (pts - best_point) @ best_normal
        inliers = np.abs(signed) < threshold

        # Определяем «верхнюю» сторону (там объект — больше не-плоских точек)
        non_plane = signed[~inliers]
        obj_above = (non_plane > 0).sum()
        obj_below = (non_plane < 0).sum()

        if obj_above >= obj_below:
            # Объект сверху: удалить inliers + всё что чётко ниже плоскости.
            # НЕ трогаем точки у основания объекта (signed ≈ 0+) — иначе
            # срезаем дно объекта, лежащего на столе.
            clearly_below = signed < -threshold * 3
            keep = ~inliers & ~clearly_below
        else:
            clearly_above = signed > threshold * 3
            keep = ~inliers & ~clearly_above

        n_removed = int((~keep).sum())
        logger.info("  Ground plane: inliers=%.1f%%, removed=%d (%.1f%%), kept=%d",
                    inlier_frac * 100, n_removed, n_removed / n * 100, int(keep.sum()))

        pc.points = pts[keep]
        norms = np.asarray(pc.normals)
        if len(norms) == n:
            pc.normals = norms[keep]
        cols = np.asarray(pc.colors)
        if len(cols) == n:
            pc.colors = cols[keep]

    def _radius_outlier_removal(self, pc, radius: float, nb_points: int):
        """
        Удаляет точки у которых меньше nb_points соседей в радиусе radius.
        Использует scipy cKDTree с параллельными воркерами.
        """
        from scipy.spatial import cKDTree
        pts = np.asarray(pc.points, dtype=np.float64)
        n = len(pts)
        if n < nb_points + 1:
            return pc
        tree = cKDTree(pts)
        # counts включает саму точку → нужно >= nb_points + 1
        counts = tree.query_ball_point(pts, r=radius,
                                       return_length=True, workers=-1)
        mask = counts >= nb_points + 1
        pc.points = pts[mask]
        norms = np.asarray(pc.normals)
        if len(norms) == n:
            pc.normals = norms[mask]
        cols = np.asarray(pc.colors)
        if len(cols) == n:
            pc.colors = cols[mask]
        return pc

    def _estimate_voxel_size(self, pc) -> float:
        """Оценить размер вокселя для downsample до ~max_points точек."""
        bb = pc.bounding_box()
        size = bb.max - bb.min
        dims = size[size > 0]
        volume = float(np.prod(dims)) if len(dims) == 3 else float(np.prod(size + 1e-6))
        return max(1e-6, (volume / self.config.max_points) ** (1.0 / 3.0) * 1.5)
