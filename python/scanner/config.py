"""Конфигурация пайплайна сканирования."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VideoConfig:
    """Параметры умного экстрактора кадров."""
    target_frames: int   = 300
    min_frames:    int   = 50
    max_frames:    int   = 800
    blur_threshold: float = 100.0   # минимальная variance Laplacian
    min_difference: float = 0.03    # нижняя граница нормализованного MSE
    max_difference: float = 0.50    # верхняя граница (сцена резко сменилась)
    sample_every_n: int   = 3       # брать каждый N-й кадр
    jpeg_quality:   int   = 90


@dataclass
class ExtractResult:
    """Итог работы VideoFrameExtractor."""
    paths:             list[Path]
    total_frames:      int          # всего кадров в видео
    sampled_frames:    int          # проверено кадров (каждый sample_every_n)
    passed_sharpness:  int          # прошли тест резкости
    passed_uniqueness: int          # прошли тест уникальности (до прореживания)
    thinned:           bool         # применялось ли равномерное прореживание
    retried:           bool         # был ли повторный проход с мягкими порогами

    @property
    def count(self) -> int:
        return len(self.paths)


@dataclass
class ScanConfig:
    input_type: str = "auto"
    colmap_path: str = r"tools\colmap\COLMAP.bat"

    # Видео-экстрактор
    video_target_frames: int = 300
    video_min_frames: int = 50
    video_max_frames: int = 800
    video_blur_threshold: float = 100.0
    video_min_difference: float = 0.03
    video_max_difference: float = 0.5
    video_sample_every_n: int = 3

    # COLMAP
    # quality="low" по умолчанию — пока не доказано что нужно больше.
    # Разница: low ~5 мин, medium ~30 мин, high ~2+ часа (на 21 Mpx снимках)
    colmap_quality: str = "low"
    colmap_matcher: str = "auto"
    colmap_sequential_overlap: int = 10
    # geom_consistency управляется через quality profile (low=false, medium/high=true)

    # Облако точек
    remove_ground_plane: bool = False   # RANSAC: удалить стол/пол перед DBSCAN
    outlier_k: int = 20
    outlier_std: float = 3.0
    # Radius Outlier Removal: удалить точки у которых < ror_nb_points соседей
    # в радиусе = dbscan_eps * ror_radius_factor.
    # Маленький factor (0.2) = только изолированные точки; больше = удаляет кластеры.
    ror_nb_points: int = 6
    ror_radius_factor: float = 0.2
    # dbscan_eps_factor: eps = (bbox_diagonal / sqrt(N)) * factor
    # Чем больше — тем крупнее кластеры; 3.0 хорошо для плотных облаков
    dbscan_eps_factor: float = 4.0
    dbscan_eps: float = 0.02        # fallback если нет точек
    dbscan_min_pts: int = 20
    # Принимать кластеры >= fraction * largest (0 → только наибольший)
    # 0.05 сохраняет внутренние изгибы ракушки как отдельный кластер
    dbscan_min_cluster_fraction: float = 0.05
    max_points: int = 500_000       # порог для voxel downsample (>5M сейчас)

    # Meshing
    poisson_depth: int = 9
    poisson_trim: float = 7.0       # trim threshold Poisson (выше = агрессивнее обрезка)

    # Ремонт
    merge_threshold: float = 1e-6
    max_hole_edges: int = 100       # add_flat_base теперь закрывает все крупные дыры
    smooth_iterations: int = 1
    smooth_lambda: float = 0.5

    # Печать
    target_height_mm: float = 100.0
    add_base: bool = True
    base_thickness_mm: float = 1.0   # толщина диска-подставки (мм, после масштаба)
    base_cut_depth_mm: float = 2.0   # срез снизу для плоского дна перед диском
    stand_radius_fraction: float = 0.9
    auto_orient: bool = True

    # Экспорт
    output_format: str = "stl"
    save_intermediate: bool = True

    def colmap_bat(self, project_root: Path) -> Path:
        return project_root / self.colmap_path
