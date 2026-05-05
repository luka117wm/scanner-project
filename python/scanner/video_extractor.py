"""Шаг 0: умный экстрактор кадров из видео (резкость + уникальность)."""
from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from .config import ExtractResult, VideoConfig

logger = logging.getLogger(__name__)

# Размер превью для быстрого вычисления MSE (не трогает оригинальный кадр)
_CMP_W, _CMP_H = 320, 180


class VideoFrameExtractor:
    """Шаг 0 пайплайна: видео → отобранные JPEG-кадры.

    Алгоритм одного прохода:
      1. Каждый config.sample_every_n кадр
      2. Фильтр резкости  : Laplacian-variance > blur_threshold
      3. Фильтр уникальности: min_diff < нормализованный MSE < max_diff
         (сравнивается с последним принятым кадром)
    После прохода:
      4. < min_frames → повтор с ослабленными порогами
      5. > max_frames → равномерное прореживание (np.linspace)
      6. Сохранить JPEG (frame_XXXX.jpg)
    """

    def extract(
        self,
        video_path: Path,
        output_dir: Path,
        config: VideoConfig = VideoConfig(),
    ) -> ExtractResult:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise OSError(f"Не удалось открыть видео: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        try:
            candidates, stats = self._filter_frames(cap, config)
        finally:
            cap.release()

        retried = False
        if len(candidates) < config.min_frames:
            logger.warning(
                "Кадров после фильтрации %d < min_frames=%d — ослабляю пороги",
                len(candidates), config.min_frames,
            )
            relaxed = VideoConfig(
                target_frames=config.target_frames,
                min_frames=config.min_frames,
                max_frames=config.max_frames,
                blur_threshold=config.blur_threshold * 0.5,
                min_difference=config.min_difference * 0.5,
                max_difference=min(config.max_difference * 1.5, 0.95),
                sample_every_n=max(1, config.sample_every_n - 1),
                jpeg_quality=config.jpeg_quality,
            )
            cap = cv2.VideoCapture(str(video_path))
            try:
                candidates, stats = self._filter_frames(cap, relaxed)
            finally:
                cap.release()
            retried = True

        thinned = False
        if len(candidates) > config.max_frames:
            indices = np.linspace(0, len(candidates) - 1, config.max_frames, dtype=int)
            candidates = [candidates[i] for i in indices]
            thinned = True
            logger.info("Прорежено до %d кадров", config.max_frames)

        output_dir.mkdir(parents=True, exist_ok=True)
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, config.jpeg_quality]
        paths: list[Path] = []
        for i, frame in enumerate(candidates):
            out_path = output_dir / f"frame_{i:04d}.jpg"
            cv2.imwrite(str(out_path), frame, encode_params)
            paths.append(out_path)

        logger.info(
            "Done: saved %d frames -> %s  "
            "(sampled=%d, sharp=%d, unique=%d, thinned=%s, retried=%s)",
            len(paths), output_dir,
            stats["sampled"], stats["sharp"], stats["unique"],
            thinned, retried,
        )
        return ExtractResult(
            paths=paths,
            total_frames=total_frames,
            sampled_frames=stats["sampled"],
            passed_sharpness=stats["sharp"],
            passed_uniqueness=stats["unique"],
            thinned=thinned,
            retried=retried,
        )

    # ------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------

    def _filter_frames(
        self,
        cap: cv2.VideoCapture,
        config: VideoConfig,
    ) -> tuple[list[np.ndarray], dict[str, int]]:
        """Один проход по видео с заданной конфигурацией."""
        candidates: list[np.ndarray] = []
        prev_small: np.ndarray | None = None
        sampled = sharp = unique = 0
        frame_idx = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if frame_idx % config.sample_every_n != 0:
                frame_idx += 1
                continue
            sampled += 1

            # --- Фильтр резкости ---
            if _sharpness(frame) < config.blur_threshold:
                frame_idx += 1
                continue
            sharp += 1

            # --- Фильтр уникальности ---
            small = cv2.resize(frame, (_CMP_W, _CMP_H))
            if prev_small is not None:
                mse = _mse(prev_small, small)
                if not (config.min_difference < mse < config.max_difference):
                    frame_idx += 1
                    continue

            unique += 1
            candidates.append(frame)
            prev_small = small
            frame_idx += 1

        return candidates, {"sampled": sampled, "sharp": sharp, "unique": unique}


# ------------------------------------------------------------------
# Вспомогательные функции (модульный уровень, легко тестировать)
# ------------------------------------------------------------------

def _sharpness(frame: np.ndarray) -> float:
    """Variance of Laplacian по серому каналу — мера резкости."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    """Нормализованный MSE ∈ [0, 1]. a, b — BGR кадры одного размера."""
    diff = a.astype(np.float32) - b.astype(np.float32)
    return float((diff ** 2).mean()) / (255.0 ** 2)
