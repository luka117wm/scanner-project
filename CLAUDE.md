# Scanner Project — Context for Claude Code

## Цель проекта

Автоматизированная система 3D-сканирования для обычных людей.
Пользователь снимает фото/видео на телефон → система выдаёт готовый STL для 3D-печати.
Без ручных шагов в MeshLab / Meshmixer.

### Актуальная архитектура (2026-05)

```
Телефон (съёмка) → Сервер-релей (хранилище/передача) → Десктоп Windows (GPU pipeline)
                                                                ↓
                                                   Десктоп 3D-редактор (Three.js)
                                                   • Ручная ориентация по осям
                                                   • Удаление шумов (интерактивно)
                                                   • Настройка подставки
                                                                ↓
                                                            STL файл
```

**Сервер** — только хранилище/релей (дешёвый VPS без GPU). GPU-вычисления — на десктопе пользователя.
**Десктоп-приложение** = pipeline (C++/Python/COLMAP) + минимальный 3D-редактор на Three.js.

## ПЛАТФОРМА: WINDOWS 10/11

> **КРИТИЧЕСКИ ВАЖНО:**
> - ОС: Windows 10/11, **БЕЗ WSL**
> - Shell: **PowerShell 7**
> - IDE: **VS Code**
> - C++: **MSVC** (Visual Studio Build Tools 2022)
> - Все пути — Windows (`D:\3ds\scanner-project\...`)
> - COLMAP — предсобранные .exe бинарники
> - Никакого bash, apt, sudo, Linux-специфичного кода

---

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                  ВХОД                                    │
│  Фотографии (20-800 JPEG/PNG)                           │
│  ИЛИ видео (.mp4/.mov/.avi) → умный экстрактор кадров   │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Python (платформа, API, CLI)                   │
│           FastAPI / CLI / WebSocket                      │
└────────────────────┬────────────────────────────────────┘
                     │ pybind11
                     ▼
┌─────────────────────────────────────────────────────────┐
│              C++ Core (_scanner_cpp.pyd)                  │
│  PointCloud: загрузка PLY, фильтрация, DBSCAN            │
│  TriangleMesh: загрузка/сохранение PLY, STL, OBJ         │
│  MeshRepair: degenerate, merge, manifold, holes, smooth   │
│  PrintPrep: cut, base, scale, orient, printability        │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  COLMAP (готовые Windows .exe)                           │
│  Путь: tools\colmap\COLMAP.bat                          │
│  Вызов: subprocess.run([colmap_bat, cmd, ...])           │
│  НЕ собираем — скачиваем с GitHub Releases               │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Веб-вьюер (Three.js) + REST API                        │
└─────────────────────────────────────────────────────────┘
```

---

## Пайплайн (10 шагов)

### Шаг 0 (видео): VideoFrameExtractor
OpenCV → фильтр резкости (Laplacian) → фильтр уникальности (MSE) → 200-500 JPEG

### Шаг 1: COLMAP
subprocess → `tools\colmap\COLMAP.bat <command>` → fused.ply
Matcher: exhaustive (<200), vocab_tree (>200), sequential (видео, overlap=10)

### Шаги 2-4: Облако (C++)
outlier removal → DBSCAN → downsample → normals

### Шаг 5: Poisson meshing (Open3D Python)

### Шаги 6-8: Ремонт (C++)
degenerate → merge → manifold → holes → smooth

### Шаг 9: Печать (C++)
orient → cut → base → scale → check

### Шаг 10: Экспорт STL

### Шаг 11 (опционально): Десктоп 3D-редактор
Three.js viewer с инструментами постобработки:
- **Align** — трансформ-гизмо для ручной ориентации модели по осям
- **Denoise** — выделение и удаление кластеров шума (лассо/bbox selection)
- **Base** — интерактивное размещение и масштабирование подставки

---

## Структура проекта

```
D:\3ds\scanner-project\
├── CLAUDE.md
├── README.md
├── .gitignore
├── .gitattributes                     # * text=auto eol=lf
│
├── tools\
│   └── colmap\                        # pre-built (НЕ в git)
│       ├── COLMAP.bat
│       ├── colmap.exe
│       └── lib\
│
├── cpp\
│   ├── CMakeLists.txt
│   ├── include\scanner\
│   │   ├── types.h
│   │   ├── point_cloud.h
│   │   ├── triangle_mesh.h
│   │   ├── mesh_repair.h
│   │   └── print_preparation.h
│   ├── src\
│   │   ├── point_cloud.cpp
│   │   ├── triangle_mesh.cpp
│   │   ├── mesh_repair.cpp
│   │   └── print_preparation.cpp
│   ├── python\
│   │   └── bindings.cpp               # → _scanner_cpp.pyd
│   ├── third_party\
│   │   └── nanoflann\nanoflann.hpp
│   └── tests\
│
├── python\
│   ├── pyproject.toml
│   ├── scanner\
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── pipeline.py
│   │   ├── video_extractor.py
│   │   ├── colmap_runner.py
│   │   ├── mesh_processor.py
│   │   ├── exporter.py
│   │   └── cli.py
│   ├── api\
│   │   ├── server.py
│   │   ├── websocket.py
│   │   └── run.py
│   └── tests\
│
├── web\
│   ├── index.html
│   ├── manifest.json
│   ├── js\ (app.js, viewer.js)
│   └── css\ (style.css)
│
├── experiments\
│   ├── run_experiments.py
│   ├── analyze_results.py
│   └── results\
│
├── docs\                              # API документации для Claude Code
├── data\                              # НЕ в git
│   ├── test_images\
│   ├── test_videos\
│   ├── workspace\
│   └── results\
└── thesis\
```

---

## Правила кодирования

### C++
- C++17, MSVC (`/std:c++17`, `/EHsc`, `/utf-8`)
- Eigen3 для линейной алгебры (через vcpkg)
- nanoflann для KD-tree (header-only)
- `#pragma once`
- `std::filesystem::path` для путей (кроссплатформенно)
- Комментарии на русском
- НЕТ POSIX: никакого `unistd.h`, `dirent.h`, `fork()`, `mmap()`
- Результат сборки: `_scanner_cpp.pyd` (Windows DLL для Python)

### Python
- Python 3.11+
- `pathlib.Path` для ВСЕХ путей (не `"D:\\folder\\file"`)
- `subprocess.run([...], shell=False)` — ВСЕГДА shell=False на Windows
- Type hints обязательны
- `logging` вместо `print`
- UTF-8: `open(path, encoding="utf-8")`

### Вызов COLMAP из Python
```python
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
colmap_bat = project_root / "tools" / "colmap" / "COLMAP.bat"

subprocess.run(
    [str(colmap_bat), "feature_extractor",
     "--database_path", str(db_path),
     "--image_path", str(image_dir),
     "--SiftExtraction.use_gpu", "1"],
    check=True,
    capture_output=True,
    text=True
)
```

---

## Сборка C++ (PowerShell)

```powershell
cd D:\3ds\scanner-project
mkdir build
cd build

cmake ..\cpp -G "Visual Studio 17 2022" -A x64 `
    -DCMAKE_PREFIX_PATH="D:\vcpkg\installed\x64-windows" `
    -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"

cmake --build . --config Release

# Результат: build\Release\_scanner_cpp.pyd
# Скопировать в python\scanner\:
Copy-Item build\Release\_scanner_cpp.pyd python\scanner\
```

---

## Установка зависимостей (PowerShell)

### Шаг 1: Инструменты
```powershell
winget install Git.Git
winget install Kitware.CMake
winget install Python.Python.3.11
winget install Microsoft.VisualStudioCode
```

### Шаг 2: Visual Studio Build Tools
Скачать Visual Studio Installer → "Desktop development with C++"
Компоненты: MSVC v143, Windows 11 SDK, CMake tools for Windows

### Шаг 3: vcpkg + Eigen3
```powershell
cd D:\
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install eigen3:x64-windows
```

### Шаг 4: Python venv
```powershell
cd D:\3ds\scanner-project
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install numpy scipy open3d trimesh pymeshfix
pip install opencv-python-headless
pip install fastapi uvicorn python-multipart websockets
pip install pybind11 scikit-learn numpy-stl pillow matplotlib
```

### Шаг 5: COLMAP
1. Скачать: https://github.com/colmap/colmap/releases
2. Взять `COLMAP-3.x-windows-cuda.zip` (NVIDIA GPU) или `no-cuda`
3. Распаковать в `tools\colmap\`
4. Проверить: `.\tools\colmap\COLMAP.bat -h`

---

## Конфигурация

```python
@dataclass
class ScanConfig:
    input_type: str = "auto"
    colmap_path: str = r"tools\colmap\COLMAP.bat"
    # ... (полный список в python\scanner\config.py)
```

---

## CLI

```powershell
python -m scanner scan --images .\photos --output model.stl
python -m scanner scan --video recording.mp4 --output model.stl --frames 500
python -m scanner extract-frames --video recording.mp4 --output .\frames\
python -m scanner process-cloud --input fused.ply --output model.stl
python -m scanner serve --host 0.0.0.0 --port 8000
```

---

## Контекст: дипломная работа

Тема: «Разработка автоматизированной системы получения 3D-моделей
для аддитивного производства методом фотограмметрии»

Эксперименты:
1. Влияние количества фотографий
2. Видео vs фото
3. Сравнение методов meshing
4. Эффективность автосегментации
5. Качество ремонта меша
