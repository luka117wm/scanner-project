"""Тест ColmapRunner — проверка формирования команд через mock subprocess."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# Убеждаемся, что python/ в пути
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scanner.colmap_runner import ColmapRunner, _PROJECT_ROOT
from scanner.config import ScanConfig


# ── Фикстуры ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner() -> ColmapRunner:
    return ColmapRunner(ScanConfig())


def _fake_result(returncode: int = 0) -> MagicMock:
    r = MagicMock()
    r.returncode = returncode
    r.stdout = ""
    r.stderr = ""
    return r


# ── Формирование команд ────────────────────────────────────────────────────────

class TestRunCmd:
    def test_uses_colmap_bat(self, runner: ColmapRunner, tmp_path: Path) -> None:
        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._run_cmd("feature_extractor", "--database_path", "db.db")

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == str(runner.colmap_bat)
        assert cmd[1] == "feature_extractor"

    def test_shell_false(self, runner: ColmapRunner) -> None:
        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._run_cmd("test_step")

        kwargs = mock_run.call_args[1]
        # shell= не передаётся явно → по умолчанию False, либо не указано совсем
        assert kwargs.get("shell", False) is False

    def test_check_true(self, runner: ColmapRunner) -> None:
        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._run_cmd("test_step")

        assert mock_run.call_args[1].get("check") is True

    def test_encoding_utf8(self, runner: ColmapRunner) -> None:
        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._run_cmd("test_step")

        assert mock_run.call_args[1].get("encoding") == "utf-8"


# ── Выбор matcher ──────────────────────────────────────────────────────────────

class TestSelectMatcher:
    def test_auto_few_photos_exhaustive(self, runner: ColmapRunner) -> None:
        assert runner._select_matcher(50,  "photos") == "exhaustive"
        assert runner._select_matcher(200, "photos") == "exhaustive"

    def test_auto_many_photos_vocab_tree(self, runner: ColmapRunner) -> None:
        assert runner._select_matcher(201, "photos") == "vocab_tree"
        assert runner._select_matcher(500, "photos") == "vocab_tree"

    def test_auto_video_sequential(self, runner: ColmapRunner) -> None:
        assert runner._select_matcher(100, "video") == "sequential"
        assert runner._select_matcher(500, "video") == "sequential"

    def test_manual_override(self) -> None:
        cfg = ScanConfig(colmap_matcher="exhaustive")
        r = ColmapRunner(cfg)
        assert r._select_matcher(999, "photos") == "exhaustive"
        assert r._select_matcher(999, "video")  == "exhaustive"


# ── Флаги качества ────────────────────────────────────────────────────────────

class TestQualityFlags:
    def test_low(self) -> None:
        r = ColmapRunner(ScanConfig(colmap_quality="low"))
        flags = r._quality_flags()
        assert "--SiftExtraction.max_num_features" in flags
        idx = flags.index("--SiftExtraction.max_num_features")
        assert flags[idx + 1] == "4096"

    def test_medium(self) -> None:
        r = ColmapRunner(ScanConfig(colmap_quality="medium"))
        assert "8192" in r._quality_flags()

    def test_high(self) -> None:
        r = ColmapRunner(ScanConfig(colmap_quality="high"))
        assert "16384" in r._quality_flags()


# ── feature_extractor ─────────────────────────────────────────────────────────

class TestFeatureExtractor:
    def test_command_structure(self, runner: ColmapRunner, tmp_path: Path) -> None:
        db   = tmp_path / "database.db"
        imgs = tmp_path / "images"
        imgs.mkdir()

        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._feature_extractor(db, imgs)

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "feature_extractor"
        assert "--database_path" in cmd
        assert str(db) in cmd
        assert "--image_path" in cmd
        assert str(imgs) in cmd
        assert "--SiftExtraction.use_gpu" in cmd

    def test_paths_are_strings(self, runner: ColmapRunner, tmp_path: Path) -> None:
        db   = tmp_path / "database.db"
        imgs = tmp_path / "images"
        imgs.mkdir()

        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._feature_extractor(db, imgs)

        cmd = mock_run.call_args[0][0]
        # Все элементы команды должны быть str, не Path
        assert all(isinstance(x, str) for x in cmd), \
            f"Не-str аргументы: {[x for x in cmd if not isinstance(x, str)]}"


# ── Matchers ──────────────────────────────────────────────────────────────────

class TestMatchCommands:
    def test_exhaustive_command(self, runner: ColmapRunner, tmp_path: Path) -> None:
        db = tmp_path / "database.db"

        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._match("exhaustive", db, "photos")

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "exhaustive_matcher"
        assert str(db) in cmd

    def test_sequential_command(self, runner: ColmapRunner, tmp_path: Path) -> None:
        db = tmp_path / "database.db"

        with patch("subprocess.run", return_value=_fake_result()) as mock_run:
            runner._match("sequential", db, "video")

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "sequential_matcher"
        assert "--SequentialMatching.overlap" in cmd
        assert str(runner.config.colmap_sequential_overlap) in cmd

    def test_vocab_tree_fallback_to_exhaustive(
        self, runner: ColmapRunner, tmp_path: Path
    ) -> None:
        db = tmp_path / "database.db"

        with patch("subprocess.run", return_value=_fake_result()) as mock_run, \
             patch.object(runner, "_find_vocab_tree", return_value=None):
            runner._match("vocab_tree", db, "photos")

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "exhaustive_matcher"

    def test_vocab_tree_with_tree_file(
        self, runner: ColmapRunner, tmp_path: Path
    ) -> None:
        db        = tmp_path / "database.db"
        tree_file = tmp_path / "vocab_tree_words32k.bin"
        tree_file.write_bytes(b"\x00")

        with patch("subprocess.run", return_value=_fake_result()) as mock_run, \
             patch.object(runner, "_find_vocab_tree", return_value=tree_file):
            runner._match("vocab_tree", db, "photos")

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "vocab_tree_matcher"
        assert "--VocabTreeMatching.vocab_tree_path" in cmd
        assert str(tree_file) in cmd

    def test_unknown_matcher_raises(
        self, runner: ColmapRunner, tmp_path: Path
    ) -> None:
        with pytest.raises(ValueError, match="Неизвестный matcher"):
            runner._match("bogus", tmp_path / "db.db", "photos")


# ── Полный пайплайн — порядок вызовов ─────────────────────────────────────────

class TestPipelineOrder:
    def _make_fake_run(self, fused_ply: Path):
        """subprocess.run возвращает успех; при stereo_fusion создаёт fused.ply."""
        def side_effect(cmd, **kwargs):
            if "stereo_fusion" in cmd:
                fused_ply.parent.mkdir(parents=True, exist_ok=True)
                fused_ply.write_bytes(b"ply")
            return _fake_result()
        return side_effect

    def test_step_order(self, runner: ColmapRunner, tmp_path: Path) -> None:
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        # Создаём 5 фейковых изображений
        for i in range(5):
            (image_dir / f"img_{i:03d}.jpg").write_bytes(b"\xff\xd8")

        workspace = tmp_path / "ws"
        fused_ply = workspace / "dense" / "fused.ply"

        with patch("subprocess.run",
                   side_effect=self._make_fake_run(fused_ply)) as mock_run:
            result = runner.run(image_dir, workspace, input_type="photos")

        # Порядок команд
        steps = [c[0][0][1] for c in mock_run.call_args_list]
        assert steps == [
            "feature_extractor",
            "exhaustive_matcher",   # 5 < 200 → exhaustive
            "mapper",
            "image_undistorter",
            "patch_match_stereo",
            "stereo_fusion",
        ]

        assert result.fused_ply == fused_ply
        assert result.matcher_used == "exhaustive"
        assert result.n_images == 5

    def test_video_uses_sequential(self, runner: ColmapRunner, tmp_path: Path) -> None:
        image_dir = tmp_path / "frames"
        image_dir.mkdir()
        for i in range(10):
            (image_dir / f"frame_{i:04d}.jpg").write_bytes(b"\xff\xd8")

        workspace = tmp_path / "ws"
        fused_ply = workspace / "dense" / "fused.ply"

        with patch("subprocess.run",
                   side_effect=self._make_fake_run(fused_ply)) as mock_run:
            result = runner.run(image_dir, workspace, input_type="video")

        steps = [c[0][0][1] for c in mock_run.call_args_list]
        assert "sequential_matcher" in steps
        assert result.matcher_used == "sequential"
