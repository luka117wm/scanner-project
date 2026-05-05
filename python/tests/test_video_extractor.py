"""Тесты VideoFrameExtractor с синтетическими видео (без реальных файлов)."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from scanner.config import VideoConfig
from scanner.video_extractor import VideoFrameExtractor, _mse, _sharpness


# ---------------------------------------------------------------------------
# Вспомогательная функция: создание синтетического .mp4
# ---------------------------------------------------------------------------

def _make_video(path: Path, n_frames: int = 60, fps: int = 30) -> None:
    """640×480 mp4: плавно меняющийся фон + случайный шум для резкости."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, float(fps), (640, 480))
    assert writer.isOpened(), f"VideoWriter не открылся для {path}"

    rng = np.random.default_rng(42)
    for i in range(n_frames):
        # Цвет медленно меняется от сине-зелёного к красному
        base = np.full((480, 640, 3), [
            min(255, i * 4),
            max(0, 255 - i * 4),
            128,
        ], dtype=np.uint8)
        noise = rng.integers(0, 40, (480, 640, 3), dtype=np.uint8)
        frame = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        writer.write(frame)

    writer.release()


# ---------------------------------------------------------------------------
# Тесты вспомогательных функций
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_sharpness_noisy_is_high(self) -> None:
        rng = np.random.default_rng(0)
        noisy = rng.integers(0, 256, (480, 640, 3), dtype=np.uint8)
        assert _sharpness(noisy) > 500.0

    def test_sharpness_solid_is_low(self) -> None:
        solid = np.full((480, 640, 3), 128, dtype=np.uint8)
        assert _sharpness(solid) < 1.0

    def test_mse_identical_is_zero(self) -> None:
        frame = np.ones((180, 320, 3), dtype=np.uint8) * 100
        assert _mse(frame, frame) == pytest.approx(0.0)

    def test_mse_opposite_is_one(self) -> None:
        a = np.zeros((180, 320, 3), dtype=np.uint8)
        b = np.full((180, 320, 3), 255, dtype=np.uint8)
        assert _mse(a, b) == pytest.approx(1.0)

    def test_mse_symmetric(self) -> None:
        rng = np.random.default_rng(7)
        a = rng.integers(0, 256, (180, 320, 3), dtype=np.uint8)
        b = rng.integers(0, 256, (180, 320, 3), dtype=np.uint8)
        assert _mse(a, b) == pytest.approx(_mse(b, a))


# ---------------------------------------------------------------------------
# Тесты VideoFrameExtractor
# ---------------------------------------------------------------------------

class TestVideoFrameExtractor:
    # Мягкая конфигурация — пропускает почти все кадры
    _PERMISSIVE = VideoConfig(
        target_frames=50,
        min_frames=1,
        max_frames=200,
        blur_threshold=5.0,
        min_difference=0.0001,
        max_difference=0.99,
        sample_every_n=1,
    )

    def test_basic_returns_result(self, tmp_path: Path) -> None:
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=60)

        result = VideoFrameExtractor().extract(video, tmp_path / "out", self._PERMISSIVE)

        assert result.count > 0
        assert result.total_frames == 60
        assert result.sampled_frames > 0
        assert result.passed_sharpness <= result.sampled_frames
        assert result.passed_uniqueness <= result.passed_sharpness

    def test_output_files_exist(self, tmp_path: Path) -> None:
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=30)
        out = tmp_path / "frames"

        result = VideoFrameExtractor().extract(video, out, self._PERMISSIVE)

        assert out.is_dir()
        for p in result.paths:
            assert p.exists()
            assert p.suffix == ".jpg"

    def test_frame_naming(self, tmp_path: Path) -> None:
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=30)

        result = VideoFrameExtractor().extract(video, tmp_path / "out", self._PERMISSIVE)

        for i, p in enumerate(result.paths):
            assert p.name == f"frame_{i:04d}.jpg", f"Неверное имя: {p.name}"

    def test_thinning_applied(self, tmp_path: Path) -> None:
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=60)

        cfg = VideoConfig(
            min_frames=1, max_frames=5,
            blur_threshold=5.0, min_difference=0.0001, max_difference=0.99,
            sample_every_n=1,
        )
        result = VideoFrameExtractor().extract(video, tmp_path / "out", cfg)

        assert result.count <= 5
        assert result.thinned is True

    def test_retry_with_strict_blur(self, tmp_path: Path) -> None:
        """Нереально строгий порог резкости → мало кадров → retry."""
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=60)

        cfg = VideoConfig(
            min_frames=5,
            blur_threshold=1e9,   # ни один кадр не пройдёт первый раз
            min_difference=0.0001,
            max_difference=0.99,
            sample_every_n=1,
        )
        result = VideoFrameExtractor().extract(video, tmp_path / "out", cfg)

        assert result.retried is True

    def test_nonexistent_video_raises(self, tmp_path: Path) -> None:
        with pytest.raises(OSError):
            VideoFrameExtractor().extract(
                tmp_path / "ghost.mp4", tmp_path / "out"
            )

    def test_output_dir_created(self, tmp_path: Path) -> None:
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=15)

        nested = tmp_path / "a" / "b" / "c"
        assert not nested.exists()

        VideoFrameExtractor().extract(video, nested, self._PERMISSIVE)
        assert nested.is_dir()

    def test_sample_every_n_reduces_sampled(self, tmp_path: Path) -> None:
        video = tmp_path / "v.mp4"
        _make_video(video, n_frames=60)

        cfg_n1 = VideoConfig(
            min_frames=1, max_frames=200,
            blur_threshold=5.0, min_difference=0.0001, max_difference=0.99,
            sample_every_n=1,
        )
        cfg_n5 = VideoConfig(
            min_frames=1, max_frames=200,
            blur_threshold=5.0, min_difference=0.0001, max_difference=0.99,
            sample_every_n=5,
        )
        r1 = VideoFrameExtractor().extract(video, tmp_path / "o1", cfg_n1)
        r5 = VideoFrameExtractor().extract(video, tmp_path / "o5", cfg_n5)

        assert r5.sampled_frames < r1.sampled_frames
