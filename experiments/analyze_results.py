"""Анализ результатов экспериментов: графики, таблицы для диплома."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).parent / "results"


def plot_photo_count() -> None:
    """График качества vs количество фото."""
    # TODO: загрузить CSV из results/, построить график
    raise NotImplementedError


if __name__ == "__main__":
    pass
