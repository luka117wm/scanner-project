"""Запуск экспериментов для дипломной работы."""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "results"


def experiment_photo_count() -> None:
    """Эксперимент 1: влияние количества фотографий на качество модели."""
    # TODO: прогнать пайплайн для N=[20, 50, 100, 200, 400, 800]
    raise NotImplementedError


def experiment_video_vs_photo() -> None:
    """Эксперимент 2: видео vs фото при одинаковом числе кадров."""
    raise NotImplementedError


def experiment_meshing_methods() -> None:
    """Эксперимент 3: сравнение методов meshing (Poisson vs BPA)."""
    raise NotImplementedError


def experiment_autosegmentation() -> None:
    """Эксперимент 4: эффективность автосегментации (DBSCAN)."""
    raise NotImplementedError


def experiment_mesh_repair() -> None:
    """Эксперимент 5: качество ремонта меша."""
    raise NotImplementedError


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    RESULTS_DIR.mkdir(exist_ok=True)
