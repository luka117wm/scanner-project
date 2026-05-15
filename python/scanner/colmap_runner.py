"""Шаг 1: обёртка вокруг COLMAP.bat (subprocess, shell=False)."""
from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .config import ScanConfig

logger = logging.getLogger(__name__)

# colmap_runner.py живёт в  python/scanner/ → parents[2] = корень проекта
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# ── Результат ─────────────────────────────────────────────────────────────────

@dataclass
class ColmapResult:
    fused_ply:   Path
    sparse_dir:  Path
    dense_dir:   Path
    n_images:    int
    matcher_used: str


# ── Основной класс ─────────────────────────────────────────────────────────────

class ColmapRunner:
    """
    Запускает COLMAP-пайплайн:
      feature_extractor → matcher → mapper → undistorter → stereo → fusion
    Возвращает путь к fused.ply.
    """

    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self.colmap_bat = _PROJECT_ROOT / config.colmap_path

    # ── Публичный метод ───────────────────────────────────────────────────────

    def run(
        self,
        image_dir: Path,
        workspace: Path,
        input_type: Literal["photos", "video"] = "photos",
    ) -> ColmapResult:
        """
        Полный пайплайн COLMAP. Возвращает ColmapResult с путём к fused.ply.
        Все промежуточные данные сохраняются в workspace/.
        """
        workspace = workspace.resolve()
        image_dir = image_dir.resolve()
        workspace.mkdir(parents=True, exist_ok=True)

        db_path    = workspace / "database.db"
        sparse_dir = workspace / "sparse"
        dense_dir  = workspace / "dense"
        fused_ply  = dense_dir / "fused.ply"

        sparse_dir.mkdir(exist_ok=True)

        n_images = self._count_images(image_dir)
        logger.info("COLMAP: %d images in %s", n_images, image_dir)

        matcher = self._select_matcher(n_images, input_type)
        logger.info("COLMAP matcher: %s", matcher)

        self._feature_extractor(db_path, image_dir)
        self._match(matcher, db_path, input_type)
        self._mapper(db_path, image_dir, sparse_dir)
        self._image_undistorter(image_dir, sparse_dir, dense_dir)
        self._patch_match_stereo(dense_dir)
        self._stereo_fusion(dense_dir, fused_ply)

        if not fused_ply.exists():
            raise FileNotFoundError(f"COLMAP не создал fused.ply: {fused_ply}")

        logger.info("COLMAP завершён: %s (%.1f MB)", fused_ply,
                    fused_ply.stat().st_size / 1e6)
        return ColmapResult(
            fused_ply=fused_ply,
            sparse_dir=sparse_dir,
            dense_dir=dense_dir,
            n_images=n_images,
            matcher_used=matcher,
        )

    # ── Шаги пайплайна ────────────────────────────────────────────────────────

    def _feature_extractor(self, db_path: Path, image_dir: Path) -> None:
        q = self._quality_profile()
        logger.info("COLMAP: feature_extractor (quality=%s, max_image_size=%s)",
                    self.config.colmap_quality, q["feat_max_image_size"])
        self._run_cmd(
            "feature_extractor",
            "--database_path",                    str(db_path),
            "--image_path",                       str(image_dir),
            "--FeatureExtraction.use_gpu",        "1",
            "--FeatureExtraction.max_image_size", q["feat_max_image_size"],
            "--SiftExtraction.max_num_features",  q["max_num_features"],
        )

    def _match(
        self,
        matcher: str,
        db_path: Path,
        input_type: str,
    ) -> None:
        logger.info("COLMAP: %s", matcher)

        if matcher == "exhaustive":
            self._run_cmd(
                "exhaustive_matcher",
                "--database_path", str(db_path),
            )

        elif matcher == "sequential":
            overlap = str(self.config.colmap_sequential_overlap)
            self._run_cmd(
                "sequential_matcher",
                "--database_path",                str(db_path),
                "--SequentialMatching.overlap",   overlap,
                "--SequentialMatching.loop_detection", "1",
            )

        elif matcher == "vocab_tree":
            vocab_tree = self._find_vocab_tree()
            if vocab_tree is None:
                logger.warning(
                    "vocab_tree_matcher: файл словаря не найден, "
                    "использую exhaustive_matcher"
                )
                self._run_cmd(
                    "exhaustive_matcher",
                    "--database_path", str(db_path),
                )
            else:
                self._run_cmd(
                    "vocab_tree_matcher",
                    "--database_path",                          str(db_path),
                    "--VocabTreeMatching.vocab_tree_path",      str(vocab_tree),
                )
        else:
            raise ValueError(f"Неизвестный matcher: {matcher!r}")

    def _mapper(
        self, db_path: Path, image_dir: Path, sparse_dir: Path
    ) -> None:
        logger.info("COLMAP: mapper")
        self._run_cmd(
            "mapper",
            "--database_path",                      str(db_path),
            "--image_path",                         str(image_dir),
            "--output_path",                        str(sparse_dir),
            "--Mapper.multiple_models",             "0",   # one model, no sparse/1 fragments
            "--Mapper.init_min_num_inliers",        "50",  # default 100 — accept weaker init pairs
            "--Mapper.abs_pose_min_num_inliers",    "15",  # default 30 — register more images
            "--Mapper.filter_min_tri_angle",        "1.0", # default 1.5 deg — keep shallow angles
        )
        # Log how many images actually ended up in sparse/0
        model_dir = sparse_dir / "0"
        if model_dir.exists():
            img_bin = model_dir / "images.bin"
            if img_bin.exists():
                import struct
                with open(img_bin, "rb") as f:
                    n = struct.unpack("<Q", f.read(8))[0]
                logger.info("COLMAP mapper: registered %d images in sparse/0", n)

    def _image_undistorter(
        self, image_dir: Path, sparse_dir: Path, dense_dir: Path
    ) -> None:
        logger.info("COLMAP: image_undistorter")
        # mapper пишет модель в sparse/0/
        model_dir = sparse_dir / "0"
        dense_dir.mkdir(exist_ok=True)
        self._run_cmd(
            "image_undistorter",
            "--image_path",  str(image_dir),
            "--input_path",  str(model_dir),
            "--output_path", str(dense_dir),
            "--output_type", "COLMAP",
        )

    def _patch_match_stereo(self, dense_dir: Path) -> None:
        q = self._quality_profile()
        geom = q["geom_consistency"]
        logger.info(
            "COLMAP: patch_match_stereo (max_image_size=%s, iters=%s, geom=%s)",
            q["pms_max_image_size"], q["num_iterations"], geom,
        )
        self._run_cmd(
            "patch_match_stereo",
            "--workspace_path",                    str(dense_dir),
            "--workspace_format",                  "COLMAP",
            "--PatchMatchStereo.gpu_index",        "0",
            "--PatchMatchStereo.max_image_size",   q["pms_max_image_size"],
            "--PatchMatchStereo.window_radius",    q["window_radius"],
            "--PatchMatchStereo.num_iterations",   q["num_iterations"],
            "--PatchMatchStereo.geom_consistency", geom,
        )

    def _stereo_fusion(self, dense_dir: Path, fused_ply: Path) -> None:
        q = self._quality_profile()
        # geom_consistency=false → only photometric depth maps exist
        input_type = "geometric" if q["geom_consistency"] == "true" else "photometric"
        logger.info("COLMAP: stereo_fusion (input_type=%s) → %s", input_type, fused_ply)
        self._run_cmd(
            "stereo_fusion",
            "--workspace_path",   str(dense_dir),
            "--workspace_format", "COLMAP",
            "--input_type",       input_type,
            "--output_path",      str(fused_ply),
        )

    def poisson_mesh(
        self,
        input_ply: Path,
        output_ply: Path,
        depth: int = 9,
        trim: float = 7.0,
    ) -> None:
        """Poisson surface reconstruction via COLMAP built-in poisson_mesher."""
        logger.info("COLMAP: poisson_mesher depth=%d %s -> %s",
                    depth, input_ply.name, output_ply.name)
        self._run_cmd(
            "poisson_mesher",
            "--input_path",              str(input_ply),
            "--output_path",             str(output_ply),
            "--PoissonMeshing.depth",    str(depth),
            "--PoissonMeshing.trim",     str(trim),
        )

    # ── Вспомогательные методы ────────────────────────────────────────────────

    def _run_cmd(self, *args: str) -> None:
        """Запустить COLMAP.bat с заданными аргументами."""
        cmd = [str(self.colmap_bat), *args]
        logger.debug("$ %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            for line in stdout.splitlines():
                logger.error("[colmap] %s", line)
            for line in stderr.splitlines():
                logger.error("[colmap stderr] %s", line)
            raise RuntimeError(
                f"COLMAP {args[0]} failed (rc={exc.returncode})"
            ) from exc
        if result.stdout:
            for line in result.stdout.splitlines():
                logger.debug("[colmap] %s", line)
        if result.stderr:
            for line in result.stderr.splitlines():
                logger.debug("[colmap stderr] %s", line)

    def _select_matcher(
        self, n_images: int, input_type: str
    ) -> str:
        """Выбрать оптимальный matcher по количеству снимков и типу входа."""
        if self.config.colmap_matcher != "auto":
            return self.config.colmap_matcher
        if input_type == "video":
            return "sequential"
        return "exhaustive" if n_images <= 200 else "vocab_tree"

    # Профили качества — единственное место где задаются параметры COLMAP.
    # PatchMatchStereo.max_image_size — КРИТИЧЕСКИЙ параметр производительности:
    # время ~ O(w * h * n_images * iterations * geom_passes)
    # 5616px vs 800px = разница в 49x по площади = ~50x по времени
    _QUALITY_PROFILES: dict[str, dict[str, str]] = {
        "low": {
            "feat_max_image_size": "1000",
            "max_num_features":    "2048",
            "pms_max_image_size":  "800",
            "window_radius":       "3",
            "num_iterations":      "3",
            "geom_consistency":    "false",   # 1 pass: 2x faster
        },
        "medium": {
            "feat_max_image_size": "1600",
            "max_num_features":    "4096",
            "pms_max_image_size":  "1200",
            "window_radius":       "5",
            "num_iterations":      "5",
            "geom_consistency":    "true",    # 2 passes: more accurate
        },
        "high": {
            "feat_max_image_size": "2400",
            "max_num_features":    "8192",
            "pms_max_image_size":  "1600",
            "window_radius":       "5",
            "num_iterations":      "7",
            "geom_consistency":    "true",
        },
    }

    def _quality_profile(self) -> dict[str, str]:
        q = self.config.colmap_quality
        profile = self._QUALITY_PROFILES.get(q)
        if profile is None:
            logger.warning("Unknown quality %r, using 'low'", q)
            profile = self._QUALITY_PROFILES["low"]
        return profile

    def _count_images(self, image_dir: Path) -> int:
        return sum(
            1 for f in image_dir.iterdir()
            if f.is_file() and f.suffix.lower() in _IMAGE_EXTS
        )

    # ── Texture export ───────────────────────────────────────────────────────────

    def texture_export(
        self,
        images_dir: Path,
        workspace: Path,
        progress_callback=None,
    ) -> Path:
        """
        Экспорт меша с текстурой через COLMAP texture_mapper.
        Возвращает путь к ZIP (model.obj + model.mtl + textures/).
        Fallback: trimesh OBJ без текстуры.
        """
        import zipfile

        def _cb(step: str, progress: float) -> None:
            if progress_callback:
                progress_callback(step, progress)

        # Pipeline кладёт данные в workspace/colmap/; legacy-путь — workspace/
        colmap_ws  = workspace / "colmap"
        tex_dir    = workspace / "texture"
        tex_dir.mkdir(exist_ok=True)

        # Найти sparse model: pipeline → colmap/sparse/0, legacy → sparse/0
        model_dir: Path | None = None
        for candidate in [colmap_ws / "sparse" / "0", workspace / "sparse" / "0"]:
            if candidate.exists():
                model_dir = candidate
                break

        # Найти dense dir: предпочесть уже готовый из pipeline, иначе создать новый
        colmap_dense = colmap_ws / "dense"
        dense_dir = colmap_dense if (colmap_dense / "images").exists() else workspace / "dense"

        # Найти текущий меш (ориентированный → отремонтированный → исходный)
        mesh_path: Path | None = None
        for name in ("mesh_oriented.ply", "mesh_fixed.ply", "mesh_repaired.ply"):
            p = workspace / "mesh" / name
            if p.exists():
                mesh_path = p
                break
        if mesh_path is None:
            raise RuntimeError("Меш не найден в workspace — запустите сканирование")

        try:
            # Undistorter — нужен только camera poses + undistorted images;
            # patch_match_stereo / stereo_fusion texture_mapper не нужны.
            if not (dense_dir / "images").exists():
                if model_dir is None:
                    raise RuntimeError("Sparse модель не найдена — запустите сканирование")
                _cb("tex_undistort", 0.2)
                dense_dir.mkdir(exist_ok=True)
                self._run_cmd(
                    "image_undistorter",
                    "--image_path",  str(images_dir),
                    "--input_path",  str(model_dir),
                    "--output_path", str(dense_dir),
                    "--output_type", "COLMAP",
                )
            else:
                _cb("tex_undistort", 0.2)

            _cb("tex_map", 0.6)
            self._run_cmd(
                "texture_mapper",
                "--workspace_path",   str(dense_dir),
                "--workspace_format", "COLMAP",
                "--input_mesh",       str(mesh_path),
                "--output_path",      str(tex_dir),
            )

            if not list(tex_dir.glob("*.obj")):
                raise RuntimeError("texture_mapper не создал .obj файл")

        except Exception as exc:
            logger.warning("COLMAP texture_mapper: %s — fallback trimesh OBJ", exc)
            _cb("tex_fallback", 0.8)
            self._export_obj_fallback(mesh_path, tex_dir)

        _cb("tex_zip", 0.95)
        zip_path = workspace / "texture_export.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in tex_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(tex_dir))

        logger.info("texture_export → %s (%.1f MB)",
                    zip_path.name, zip_path.stat().st_size / 1e6)
        return zip_path

    def _export_obj_fallback(self, mesh_path: Path, out_dir: Path) -> None:
        """Fallback: экспорт OBJ без текстуры через trimesh."""
        try:
            import trimesh as tm
            m = tm.load(str(mesh_path), force="mesh", process=False)
            m.export(str(out_dir / "model.obj"))
            logger.info("trimesh OBJ fallback → model.obj")
        except Exception as exc:
            raise RuntimeError(f"OBJ fallback failed: {exc}") from exc

    def _find_vocab_tree(self) -> Path | None:
        """Ищет файл vocab_tree рядом с COLMAP.bat."""
        colmap_dir = self.colmap_bat.parent
        patterns = ["vocab_tree*.bin", "*.bin"]
        for pattern in patterns:
            candidates = list(colmap_dir.glob(pattern))
            if candidates:
                return candidates[0]
        return None
