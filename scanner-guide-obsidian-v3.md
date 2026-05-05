# 🏗️ Руководство: 3D-сканер с Claude Code (Windows)

> [!info] Мета
> **Платформа:** Windows 10/11, VS Code, PowerShell, MSVC
> **Стек:** C++ ядро + Python + COLMAP (pre-built .exe) + Open3D
> **Инструмент:** Claude Code (CLI)
> **Связанные:** [[Дипломная работа]], [[COLMAP документация]], [[Научные статьи]]

---

## 📋 Содержание

- [[#Фаза 0 — Установка на Windows]]
- [[#Фаза 1 — Инициализация проекта]]
- [[#Фаза 2 — Извлечение кадров из видео]]
- [[#Фаза 3 — C++ ядро — облако точек]]
- [[#Фаза 4 — C++ ядро — меш и ремонт]]
- [[#Фаза 5 — C++ ядро — подготовка к печати]]
- [[#Фаза 6 — Python обёртка и пайплайн]]
- [[#Фаза 7 — REST API]]
- [[#Фаза 8 — Веб-вьюер]]
- [[#Фаза 8.5 — Десктоп 3D-редактор]]
- [[#Фаза 9 — Мобильное приложение + сервер-релей]]
- [[#Фаза 10 — Эксперименты]]
- [[#Приложение A — Документации]]
- [[#Приложение B — Troubleshooting]]
- [[#Приложение C — Научные источники]]

---

## Фаза 0 — Установка на Windows

### 0.1. Базовые инструменты

Открыть PowerShell **от администратора**:

```powershell
winget install Git.Git
winget install Kitware.CMake
winget install Python.Python.3.11
winget install Microsoft.VisualStudioCode
winget install Microsoft.PowerShell
```

Перезапустить PowerShell после установки.

### 0.2. Visual Studio Build Tools (C++ компилятор)

1. Скачать [Visual Studio Installer](https://visualstudio.microsoft.com/downloads/) → "Build Tools for Visual Studio 2022"
2. Выбрать компонент **"Desktop development with C++"**
3. Обязательно отметить: MSVC v143, Windows 11 SDK, CMake tools
4. Установить (~4 GB)

Проверка (в **Developer PowerShell for VS 2022**):
```powershell
cl.exe
# Должно показать версию компилятора
```

### 0.3. vcpkg + Eigen3

```powershell
cd D:\
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install eigen3:x64-windows
```

> [!tip] Запомнить путь
> Eigen3 будет в `D:\vcpkg\installed\x64-windows\include\eigen3`
> Для CMake: `-DCMAKE_PREFIX_PATH="D:\vcpkg\installed\x64-windows"`

### 0.4. Проект и Python venv

```powershell
mkdir D:\3ds\scanner-project
cd D:\3ds\scanner-project

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install numpy scipy open3d trimesh pymeshfix
pip install opencv-python-headless
pip install fastapi uvicorn python-multipart websockets
pip install pybind11 scikit-learn numpy-stl pillow matplotlib
```

### 0.5. COLMAP (готовые бинарники)

1. Скачать: https://github.com/colmap/colmap/releases
2. Файл `COLMAP-3.x-windows-cuda.zip` (если NVIDIA GPU) или `no-cuda`
3. Распаковать в `D:\3ds\scanner-project\tools\colmap\`
4. Проверка:

```powershell
.\tools\colmap\COLMAP.bat -h
```

> [!warning] Если нет NVIDIA GPU
> Скачайте `no-cuda` версию. Dense reconstruction будет медленнее
> (CPU), но работать будет.

### 0.6. Claude Code

```powershell
npm install -g @anthropic-ai/claude-code
claude --version
claude login
```

### 0.7. CLAUDE.md и docs

1. Положить [[CLAUDE.md]] в `D:\3ds\scanner-project\`
2. Создать `docs\` и наполнить (см. [[#Приложение A — Документации]])

```powershell
mkdir docs, data\test_images, data\test_videos, data\workspace, data\results
```

### 0.8. Тестовые данные

Снимите на телефон 30-50 фото объекта (чашка, статуэтка) или 60-сек видео.
Скопируйте в `data\test_images\` или `data\test_videos\`.

### 0.9. VS Code настройки

Установите расширения:
- C/C++ (Microsoft)
- Python (Microsoft)
- CMake Tools (Microsoft)

Файл `.vscode\settings.json`:
```json
{
    "cmake.configureArgs": [
        "-DCMAKE_PREFIX_PATH=D:/vcpkg/installed/x64-windows"
    ],
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

> [!check] Контрольная точка
> - [ ] `cl.exe` работает (из Developer PowerShell)
> - [ ] `python --version` → 3.11+
> - [ ] `cmake --version` → 3.28+
> - [ ] `.\tools\colmap\COLMAP.bat -h` → справка COLMAP
> - [ ] `claude --version` → Claude Code
> - [ ] VS Code открывает проект
> → [[Фаза 0 — Результаты]]

---

## Фаза 1 — Инициализация проекта

### Промпт 1.1 — Структура

```
Прочитай CLAUDE.md полностью.
Мы на Windows, компилятор MSVC, shell PowerShell, IDE VS Code.

Создай полную структуру проекта:
1. Все директории из CLAUDE.md "Структура проекта"
2. cpp\CMakeLists.txt:
   - cmake_minimum_required(VERSION 3.16)
   - project(scanner LANGUAGES CXX)
   - set(CMAKE_CXX_STANDARD 17)
   - find_package(Eigen3 REQUIRED)
   - find_package(pybind11 REQUIRED)
   - add_library(scanner_core STATIC src/point_cloud.cpp src/triangle_mesh.cpp ...)
   - target_link_libraries(scanner_core Eigen3::Eigen)
   - pybind11_add_module(_scanner_cpp python/bindings.cpp)
   - target_link_libraries(_scanner_cpp PRIVATE scanner_core)
   - enable_testing()
   - На Windows: target_compile_options(scanner_core PRIVATE /utf-8)
3. Скачай nanoflann.hpp в cpp\third_party\nanoflann\ 
   (или создай заглушку с комментарием где скачать)
4. python\pyproject.toml для пакета "scanner"
5. .gitignore (build/, venv/, data/, tools/, __pycache__, *.pyd, *.dll)
6. .gitattributes: * text=auto eol=lf
7. README.md

Только скелет — пустые файлы с правильными заголовками.
```

### Промпт 1.2 — Проверка сборки

```
Мы на Windows, MSVC. Проверь что проект собирается:

1. Минимальный cpp\src\point_cloud.cpp (одна функция-заглушка)
2. Минимальный cpp\include\scanner\point_cloud.h
3. Минимальный cpp\python\bindings.cpp (pybind11, функция hello() → "ok")
4. Сборка из PowerShell:
   cd D:\3ds\scanner-project
   mkdir build; cd build
   cmake ..\cpp -G "Visual Studio 17 2022" -A x64 `
       -DCMAKE_PREFIX_PATH="D:\vcpkg\installed\x64-windows" `
       -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
   cmake --build . --config Release
5. Проверка:
   cd D:\3ds\scanner-project
   $env:PYTHONPATH = "build\Release"
   python -c "import _scanner_cpp; print(_scanner_cpp.hello())"
6. Исправь все ошибки.
```

### Промпт 1.3 — Базовые типы

```
Файл: cpp\include\scanner\types.h

#pragma once
#include <Eigen/Dense>
#include <string>
#include <vector>
#include <cstdint>

using Vector3d = Eigen::Vector3d;
using Vector3i = Eigen::Vector3i;
using Matrix3d = Eigen::Matrix3d;

struct BoundingBox { ... };
struct Color { uint8_t r, g, b; };
enum class LogLevel { DEBUG, INFO, WARNING, ERROR };
void log(LogLevel, const std::string&);

Убедись что компилируется с MSVC без warnings.
```

> [!check] → [[Фаза 1 — Результаты]]

---

## Фаза 2 — Извлечение кадров из видео

### Промпт 2.1 — VideoFrameExtractor

```
Прочитай CLAUDE.md "Умный экстрактор кадров".
Мы на Windows, пути через pathlib.Path.

Файл: python\scanner\video_extractor.py
Файл: python\scanner\config.py (VideoConfig, ExtractResult)

Класс VideoFrameExtractor:
def extract(self, video_path: Path, output_dir: Path, config=VideoConfig()) -> ExtractResult:
    """
    1. cv2.VideoCapture(str(video_path))
    2. Каждый config.sample_every_n кадр
    3. Резкость: cv2.Laplacian(gray, CV_64F).var() > blur_threshold
    4. Уникальность: min_diff < MSE(prev, curr) < max_diff
    5. >max_frames → равномерное прореживание
    6. <min_frames → ослабить пороги, повтор
    7. Сохранить JPEG: cv2.imwrite(str(output_dir / f"frame_{i:04d}.jpg"), frame)
    """

Используй pathlib.Path ВЕЗДЕ. Тест с синтетическим видео.
CLI: python -m scanner extract-frames --video X.mp4 --output .\frames\ --frames 300
```

### Промпт 2.2 — Тест

```
Запусти VideoFrameExtractor. Если нет реального видео — 
создай синтетическое (cv2.VideoWriter, 100 кадров, 20 размытых, 10 дубликатов).
Выведи ExtractResult. Сохрани гистограммы в experiments\results\.
```

> [!check] → [[Фаза 2 — Результаты]]

---

## Фаза 3 — C++ ядро — облако точек

### Промпт 3.1 — PointCloud + PLY + KD-Tree

```
Прочитай CLAUDE.md и docs\ply-format-spec.md.
MSVC, Windows, std::filesystem::path для путей.

cpp\include\scanner\point_cloud.h + cpp\src\point_cloud.cpp

Класс PointCloud:
- points_, normals_, colors_
- load_ply(std::filesystem::path) — ASCII + binary little endian
- save_ply(std::filesystem::path) — binary
- size(), bounding_box(), center_to_origin()
- KD-tree (nanoflann): build_kdtree(), k_nearest(point,k), radius_search(point,r)

Для Windows: открытие файлов через std::ifstream с std::ios::binary.
Тест: 1000 точек → save → load → сравнить.
```

### Промпт 3.2 — Фильтрация

```
Добавь в PointCloud:
1. statistical_outlier_removal(k=20, std_ratio=2.0) → PointCloud
2. voxel_downsample(voxel_size) → PointCloud
3. estimate_normals(k=30) — PCA, ориентация от центра масс

Тест: сфера 5000 + 500 шум → outlier → ~5000.
```

### Промпт 3.3 — DBSCAN

```
Добавь: segment_largest_cluster(eps=0.02, min_points=50) → PointCloud
DBSCAN через radius_search(KD-tree). Вернуть самый большой кластер.
Тест: два шара + шум → largest = большой шар.
```

### Промпт 3.4 — Тест (БЕЗ COLMAP)

```
Тестируем C++ модуль на СИНТЕТИЧЕСКИХ данных (без COLMAP, без GPU):
1. Сгенерируй тор: 30000 точек + 5000 случайных выбросов
2. Сохрани как synthetic.ply
3. Загрузи через PointCloud → outlier removal → DBSCAN → normals
4. Сохрани cleaned.ply
5. Выведи статистику и тайминги каждого шага

НЕ запускай COLMAP — это отдельная фаза.
```

> [!check] → [[Фаза 3 — Результаты]]

---

## Фаза 4 — C++ ядро — меш и ремонт

### Промпт 4.1 — TriangleMesh

```
cpp\include\scanner\triangle_mesh.h + cpp\src\triangle_mesh.cpp

TriangleMesh:
- vertices_, faces_ (Vector3i), normals_, colors_
- load_ply, load_stl (binary), save_ply, save_stl (binary), save_obj
- num_vertices/faces, bounding_box, compute_normals, surface_area, volume
- is_watertight() — все рёбра в ровно 2 гранях
- build_edge_map(), find_boundary_edges(), get_vertex_neighbors(v)

Windows: std::ifstream/ofstream с std::ios::binary.
Тест: куб → save_stl → load_stl → watertight==true, volume≈1.0.
```

### Промпт 4.2 — MeshRepair

```
cpp\include\scanner\mesh_repair.h + cpp\src\mesh_repair.cpp

MeshRepair:
1. remove_degenerate_faces()
2. remove_duplicate_faces()
3. merge_close_vertices(threshold=1e-6)
4. make_manifold()
5. fill_holes(max_hole_edges=100) — boundary loops → fan triangulation
6. laplacian_smooth(iterations=3, lambda=0.5) — не двигать boundary
7. repair_all() → RepairReport

Тест: куб без одной грани → fill → watertight==true.
```

> [!check] → [[Фаза 4 — Результаты]]

---

## Фаза 5 — C++ ядро — подготовка к печати

### Промпт 5.1 — PrintPreparation

```
cpp\include\scanner\print_preparation.h + cpp\src\print_preparation.cpp

PrintPreparation:
1. cut_with_plane(point, normal) — обрезать, перетриангулировать
2. add_flat_base(thickness=2.0) — крышки + стенки
3. scale_to_size(target_mm, axis='z')
4. auto_orient() — крупнейшая грань вниз
5. check_printability() → PrintabilityReport

Тест: icosphere → cut → base → scale(50) → watertight==true.
Проверить STL через Python: trimesh.load("test.stl").is_watertight
```

> [!check] → [[Фаза 5 — Результаты]]

---

## Фаза 6 — Python обёртка и пайплайн

### Промпт 6.1 — pybind11

```
Прочитай docs\pybind11-basics.md и все C++ заголовки.

cpp\python\bindings.cpp — оберни все классы.
numpy для points/vertices/faces.
Модуль: _scanner_cpp → файл _scanner_cpp.pyd

python\scanner\__init__.py: from ._scanner_cpp import ...

Обнови CMakeLists.txt. Пересобери. Проверь:
python -c "from scanner import PointCloud; print('OK')"
```

### Промпт 6.2 — ColmapRunner (Windows)

```
Прочитай CLAUDE.md "Вызов COLMAP из Python".

python\scanner\colmap_runner.py

КРИТИЧЕСКИ ВАЖНО — мы на Windows:
- colmap_bat = project_root / "tools" / "colmap" / "COLMAP.bat"
- subprocess.run([str(colmap_bat), "feature_extractor", ...], shell=False, check=True)
- Пути передавать как str(Path(...))
- Matcher: auto-выбор (exhaustive / vocab_tree / sequential)
- Тест (mock): проверить формирование команд
```

### Промпт 6.3 — Pipeline

```
Прочитай CLAUDE.md "Пайплайн (10 шагов)".

python\scanner\pipeline.py — ScannerPipeline:
def scan(input_path, output_path, config, progress_callback) → ScanResult:
    Шаги 0-10 из CLAUDE.md.
    pathlib.Path для ВСЕХ путей.
    Промежуточные файлы в data\workspace\.

python\scanner\cli.py — argparse:
python -m scanner scan --images .\photos --output model.stl
python -m scanner scan --video video.mp4 --output model.stl --frames 500
```

### Промпт 6.4 — Poisson (Open3D)

```
python\scanner\mesh_processor.py
Open3D Poisson: read_point_cloud → create_from_point_cloud_poisson(depth=9)
→ remove low-density → save PLY
```

> [!check] → [[Фаза 6 — Результаты]]
> `python -m scanner scan --images .\photos --output model.stl` работает.

---

## Фаза 7 — REST API

### Промпт 7.1 — FastAPI

```
python\api\server.py

POST /api/scan/upload — files[] или video
POST /api/scan/{id}/start
GET  /api/scan/{id}/status
GET  /api/scan/{id}/download/stl
WS   /api/scan/{id}/ws

CORS, max 2GB upload. Пути — pathlib.Path.

python\api\run.py:
uvicorn api.server:app --host 0.0.0.0 --port 8000

Тест: curl или Invoke-WebRequest из PowerShell.
```

> [!check] → [[Фаза 7 — Результаты]]

---

## Фаза 8 — Веб-вьюер

### Промпт 8.1 — Three.js UI

```
web\index.html, web\js\app.js, web\js\viewer.js, web\css\style.css

Three.js CDN (r160+). 5 состояний:
1. UPLOAD (drag&drop, настройки, кнопка)
2. PROCESSING (прогресс WebSocket)
3. RESULT (3D-вьюер + статистика + скачивание)
4. VIEWER (OrbitControls, solid/wireframe)
5. ERROR

Тёмная тема, responsive, Inter шрифт.
```

> [!check] → [[Фаза 8 — Результаты]]

---

## Фаза 9 — PWA

### Промпт 9.1

```
manifest.json, service-worker.js.
Камера: navigator.mediaDevices.getUserMedia.
"Добавить на экран" → работает как приложение.
```

---

## Фаза 10 — Эксперименты

### Промпт 10.1 — Запуск экспериментов

```
experiments\run_experiments.py

ЭКС 1: кол-во фото (20/40/60/80/100/150/200)
ЭКС 2: видео vs фото
ЭКС 3: методы meshing (Poisson depth 8/9/10/11)
ЭКС 4: DBSCAN (eps 0.01/0.02/0.05/0.1)
ЭКС 5: ремонт (до/после: holes, manifold, watertight, Hausdorff)

CSV + matplotlib графики (PNG+PDF).
Все пути — pathlib.Path.
```

### Промпт 10.2 — Материалы диплома

```
Таблицы, графики PDF 300dpi, черновик Главы 4 (8-10 стр),
скриншоты пайплайна для Главы 3. Сохрани в thesis\.
```

> [!check] → [[Фаза 10 — Результаты экспериментов]]

---

## Приложение A — Документации

| Файл | Как получить | Фаза |
|------|-------------|------|
| `colmap-cli-reference.md` | `.\tools\colmap\COLMAP.bat -h > docs\colmap-cli.md` | 6 |
| `open3d-pointcloud-api.md` | `python -c "import open3d; help(open3d.geometry.PointCloud)" > docs\...` | 6 |
| `open3d-mesh-api.md` | `python -c "import open3d; help(open3d.geometry.TriangleMesh)" > docs\...` | 6 |
| `trimesh-api.md` | `python -c "import trimesh; help(trimesh.Trimesh)" > docs\...` | 5 |
| `pybind11-basics.md` | [pybind11.readthedocs.io](https://pybind11.readthedocs.io/en/stable/basics.html) | 6 |
| `fastapi-quickstart.md` | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/tutorial/) | 7 |
| `threejs-loaders.md` | [threejs.org/docs](https://threejs.org/docs/#examples/en/loaders/PLYLoader) | 8 |
| `ply-format-spec.md` | [Wikipedia PLY](https://en.wikipedia.org/wiki/PLY_(file_format)) | 3 |
| `stl-format-spec.md` | [Wikipedia STL](https://en.wikipedia.org/wiki/STL_(file_format)) | 5 |
| `opencv-video-api.md` | `python -c "import cv2; help(cv2.VideoCapture)" > docs\...` | 2 |
| `nanoflann-usage.md` | [github.com/jlblancoc/nanoflann](https://github.com/jlblancoc/nanoflann) | 3 |

### Генерация (PowerShell)

```powershell
cd D:\3ds\scanner-project
.\tools\colmap\COLMAP.bat -h > docs\colmap-cli-reference.md

python -c "import open3d; help(open3d.geometry.PointCloud)" > docs\open3d-pointcloud-api.md 2>&1
python -c "import open3d; help(open3d.geometry.TriangleMesh)" > docs\open3d-mesh-api.md 2>&1
python -c "import trimesh; help(trimesh.Trimesh)" > docs\trimesh-api.md 2>&1

# nanoflann (скачать вручную или через curl)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/jlblancoc/nanoflann/master/include/nanoflann.hpp" `
    -OutFile "cpp\third_party\nanoflann\nanoflann.hpp"
```

---

## Приложение B — Troubleshooting

> [!warning] "cmake не находит Eigen3"
> ```powershell
> cmake .. -DCMAKE_PREFIX_PATH="D:\vcpkg\installed\x64-windows"
> ```

> [!warning] "cmake не находит pybind11"
> ```powershell
> cmake .. -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
> ```

> [!warning] "MSVC: нет cl.exe"
> Запускайте из **Developer PowerShell for VS 2022**
> (Start → "Developer PowerShell")

> [!warning] "COLMAP крашится"
> Используйте `no-cuda` версию если нет NVIDIA GPU.
> Уменьшите `--SiftExtraction.max_image_size 1000`.

> [!warning] "_scanner_cpp.pyd не импортируется"
> Скопируйте `build\Release\_scanner_cpp.pyd` в `python\scanner\`.
> Или: `$env:PYTHONPATH = "D:\3ds\scanner-project\build\Release"`

> [!warning] "PowerShell: скрипт .ps1 не запускается"
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

> [!warning] "Claude Code не видит CLAUDE.md"
> Запускайте claude из корня проекта: `cd D:\3ds\scanner-project; claude`

---

## Приложение C — Научные источники

1. Schönberger, Frahm — Structure-from-Motion Revisited // CVPR 2016
2. Schönberger et al — Pixelwise View Selection for MVS // ECCV 2016
3. Hartley, Zisserman — Multiple View Geometry // Cambridge 2003
4. Lowe — SIFT // IJCV 2004
5. Kazhdan et al — Screened Poisson Surface Reconstruction // ACM TOG 2013
6. Bernardini et al — Ball-Pivoting Algorithm // IEEE TVCG 1999
7. Kohtala et al — Photogrammetry-based 3D scanning // Procedia CIRP 2021
8. Attene — Repairing digitized polygon meshes // Visual Computer 2010
9. Ju — Robust repair of polygonal models // ACM TOG 2004
10. Özyeşil et al — Survey of SfM // Acta Numerica 2017

→ [[Научные статьи]]

---

## Фаза 8.5 — Десктоп 3D-редактор

> [!info] Статус: В разработке (2026-05)

### Зачем

Автоматический пайплайн работает хорошо, но иногда:
- `auto_orient` ориентирует модель неверно
- Остаётся шум (трава, фон) после DBSCAN
- Подставка некорректно рассчитывается для нестандартных объектов

Решение: минимальный 3D-редактор прямо в десктопном приложении (Three.js), без MeshLab/Meshmixer.

### Инструменты редактора

| Инструмент | Описание |
|---|---|
| **Align** | Трансформ-гизмо (rotate/translate) для ручной ориентации модели |
| **Denoise** | Выделение кластеров шума (bbox/lasso selection) + удаление |
| **Base** | Интерактивное размещение диска-подставки, выбор радиуса и толщины |

### Архитектура

```
Three.js STL viewer (уже есть в web/)
    + TransformControls (rotate/translate)
    + Raycaster + SelectionBox (для denoise)
    + Disc mesh параметрический (для base)
    + Кнопка "Export STL" → Blob download или API endpoint
```

### Промпты для Claude Code

```
Фаза 8.5 Шаг 1: Добавь TransformControls в Three.js viewer.
Модель должна вращаться/двигаться мышью при зажатой клавише T.
Файл: web/js/viewer.js

Фаза 8.5 Шаг 2: Добавь SelectionBox + выделение треугольников по области.
По нажатию D + drag — выделить полигоны в области, Delete — удалить.

Фаза 8.5 Шаг 3: Добавь интерактивную подставку-диск.
Слайдеры: radius (10-90% bbox), thickness (1-10 мм).
Диск отображается в реальном времени под моделью.
По кнопке "Merge" — объединить в один STL.
```

### Новая схема развёртывания

```
Телефон → Сервер-релей (VPS, без GPU) → Десктоп (pipeline + редактор)
```

Сервер = только хранилище и очередь задач. Все GPU-вычисления — локально.

---

## Связанные заметки

- [[CLAUDE.md]]
- [[Дипломная работа]]
- [[Научные статьи]]
- [[План-график диплома]]
- [[Claude Code конфигурация]]
- [[Фаза 0 — Результаты]] … [[Фаза 10 — Результаты экспериментов]]

---

> [!summary] Итого
> **10 фаз, ~20 промптов.** Всё на Windows, PowerShell, MSVC.
> 1. Установить всё (Фаза 0)
> 2. `CLAUDE.md` + `docs\` в корне
> 3. `cd D:\3ds\scanner-project` → `claude`
> 4. Копировать промпт → Claude Code пишет + тестирует
> 5. Ошибка → дать Claude Code ошибку → исправит
