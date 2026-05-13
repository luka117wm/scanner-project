# Дневник разработки — Scanner 3D

Тема диплома: «Разработка автоматизированной системы получения 3D-моделей
для аддитивного производства методом фотограмметрии»

---

## 2026-05-13 — Фаза 11.G: нативное окно pywebview

### Новые файлы

**`python/desktop.py`** — точка входа нативного приложения:
- Запускает FastAPI (`api.server.app`) в daemon-thread через `uvicorn.run`
- Ждёт готовности сервера: поллинг `GET /api/status` с таймаутом 10 сек
- Открывает окно `webview.create_window("3D Scanner", "http://127.0.0.1:8765/", js_api=DesktopAPI(), width=1280, height=800, min_size=(800, 600))`

**`python/desktop_api.py`** — JS-API объект:
- `get_folder()` → `webview.windows[0].create_file_dialog(FOLDER_DIALOG)` → нативный диалог выбора папки

**`scripts/run_desktop.ps1`** — PowerShell-скрипт запуска:
- Активирует venv, запускает `python python\desktop.py`

### Интеграция с UI

`app.js` кнопка «Выбрать папку» уже реализована (из фазы 11.G):
```javascript
if (window.pywebview?.api?.get_folder) {
    const path = await window.pywebview.api.get_folder();
    if (path) folderPath.value = path;
} else {
    folderPath.focus(); folderPath.select();  // fallback в браузере
}
```

### Зависимости

`pip install pywebview` — установлен pywebview 6.2.1 (pythonnet, cffi, bottle).

На Windows использует WebView2 (Chromium Edge), не требует внешнего браузера.

### Режимы работы

- **Нативное окно:** `python python\desktop.py` или `.\scripts\run_desktop.ps1`
- **Браузер (отладка):** `python python\api\run.py` → `http://localhost:8765/`

### Следующие шаги

- Финальное тестирование с реальными фото
- Проверка полного UX: съёмка → pipeline → просмотр → export STL

---

## 2026-05-05 — tst5 (200 фото), ROR, фиксы пайплайна, новая архитектура

### Тестирование tst5

- Добавлен tst5 (200 SONY JPEG) в `run_e2e_test.py`
- Первый полный прогон: COLMAP зарегистрировал **200/200 фото** за 2.4 мин (exhaustive matcher)
- `patch_match_stereo` medium: ~64 мин; `stereo_fusion`: 2 мин; fused.ply = 59.3 MB, 2 195 752 точки
- Итоговый STL: watertight=True, bbox 117.9×130.6×100 мм, объём 268 658 mm³

### Исправления пайплайна

**Radius Outlier Removal (шаг 2b):**
- Добавлен между SOR и DBSCAN в `mesh_processor.py`
- Убирает scatter-шум (трава, одиночные листья) — точки у которых < `ror_nb_points` соседей в радиусе
- Ключевой параметр: `ror_radius_factor=0.2` (0.2×dbscan_eps). При factor=1.0 убирает лишь 604 точки; при 0.2 убирает 157 222 точки (7.2%) — трава уходит, поверхностные точки выживают
- `scipy` не был установлен в venv → `pip install scipy` (scikit-learn уже был)

**Сглаживание:**
- `smooth_iterations: 3 → 1` — заметно более чёткая геометрия без wash-out

**Подставка-диск (рефакторинг):**
- `scale_to_size` перенесён ДО `_add_base` — теперь `base_thickness_mm` и `base_cut_depth_mm` в реальных мм
- `base_thickness_mm: 2.0 → 1.0` (тоньше по запросу)
- Новый параметр `base_cut_depth_mm=2.0`: `cut_with_plane` срезает 2 мм снизу для плоского дна перед диском
- Проблема: `cut_with_plane` стабильно открывает рёбра на сложных мешах (288-591 open edges) → автоматический fallback на `add_flat_base`

**CLI process-cloud:**
- Timestamped workspace `workspace_YYYYMMDD_HHMMSS/` — промежуточные файлы не перезаписываются
- Лог в файл `process_cloud_TIMESTAMP.log` рядом с STL
- Исправлен UnicodeEncodeError на `³` в print (CP1251 не поддерживает)

### Новое архитектурное решение

**Отказ от GPU-сервера.** Облачный сервер с GPU слишком дорог. Новая схема:

```
Телефон → (фото/видео) → Сервер-релей (хранилище) → Десктоп (pipeline GPU)
                                                              ↓
                                                    Десктоп 3D-редактор
                                                    (align / denoise / base)
                                                              ↓
                                                           STL файл
```

Десктоп-приложение = pipeline + минимальный 3D-редактор:
1. **Align** — ручная ориентация по осям (когда auto_orient не справляется)
2. **Denoise** — интерактивное удаление шумов (выделение областей/кластеров)
3. **Base** — размещение и настройка подставки вручную

Основа: Three.js (уже в `web/`) расширяется до интерактивного редактора.

### Известные проблемы / Следующие шаги

1. `cut_with_plane` + `add_disc_stand` не работает для сложных органических мешей — всегда fallback на `add_flat_base`; нужно либо убрать cut, либо запускать pymeshfix после среза
2. ROR с factor=0.2 убирает 7% точек — результат визуально чище, но grass-кластеры частично остаются (DBSCAN дочищает)
3. Десктоп 3D-редактор: начать с Three.js viewer + трансформ-гизмо + выделение кластеров
4. vocab_tree для COLMAP (>200 фото) пока не скачан

---

## 2026-05-13 — Фазы 11.E–11.F + SQLite история сканов + тесты

### Фаза 11.E — Repair mode

**`viewer.js`:**
- `_enterRepair()` загружает меш (`GET /api/result/oriented`), делает `GET /api/edit/mesh-info`
- Тулбар показывает: `V:N F:N | Дыры:N | Watertight:Да/Нет`
- Если `open_edges > 0` — `GET /api/result/boundary-edges` → `THREE.LineSegments` красным поверх меша (до 10K рёбер)
- `[Закрыть дыры]` → `POST /api/edit/fill-holes` → перезаходит в repair-режим, обновляет инфо
- `[Smooth ×3]` → `POST /api/edit/smooth?iterations=3` → аналогично
- `_exitRepair()` → `_disposeEdges()` (удаляет LineSegments из сцены)

**`server.py` (4 новых эндпоинта):**
- `GET /api/edit/mesh-info` — trimesh вычисляет V/F/open_edges/is_watertight через `np.unique(edges_sorted, axis=0)`, volume из `m.volume`
- `GET /api/result/boundary-edges` — те же граничные рёбра как `[[x1,y1,z1,x2,y2,z2]...]`, лимит 10K
- `POST /api/edit/fill-holes` — `trimesh.repair.fill_holes` + pymeshfix → сохраняет поверх `mesh_oriented.ply`
- `POST /api/edit/smooth` — `trimesh.smoothing.filter_laplacian` → сохраняет поверх `mesh_oriented.ply`

Ключевое решение: fill-holes и smooth сохраняют результат в `mesh_oriented.ply`, а не в новый файл — `_current_mesh_path()` всегда находит его первым и цепочка orient→repair работает корректно.

### Фаза 11.F — Экспорт STL и OBJ+текстура

**STL:**
- `[Export STL]` → открывает `<dialog>` с полем высоты (мм) и чекбоксом «Подставка»
- `POST /api/export/stl {height_mm, add_base}` → `Exporter.prepare_and_export()` с `auto_orient=False` (пользователь уже ориентировал) → синхронный, сохраняет в `data/results/export_ts.stl`
- `GET /api/export/download/stl` → `FileResponse` с `Content-Disposition: attachment`
- Браузер получает скачивание через временный `<a>` элемент

**OBJ + текстура:**
- `[OBJ+tex]` → POST + SSE прогресс (отдельный `/api/export/stream`)
- `colmap_runner.py` новый метод `texture_export(images_dir, workspace, cb)`:
  - Пропускает шаги если результаты уже есть (file-based idempotency: `dense/images/`, `stereo/depth_maps/*.h5`, `dense/fused.ply`)
  - Запускает `colmap texture_mapper --input_mesh mesh_oriented.ply --output_path texture/`
  - Fallback: `trimesh.export(model.obj)` без текстуры если texture_mapper недоступен
  - Упаковывает всё в `texture_export.zip`
- `GET /api/export/download/obj` → ZIP-файл
- Отдельный `_export_state` с Lock, не смешивается со `_state` скана

**Диалог STL:** нативный `<dialog>` HTML5, тёмная тема через CSS-переменные.

### SQLite история сканов

**Проблема:** `_state` в памяти → рестарт сервера = всё забыто, кнопки экспорта не работают, `images_dir` для OBJ неизвестен.

**Решение:** `python/api/db.py` — обёртка над `sqlite3` (stdlib, без зависимостей).

Схема таблицы `scans`: `id, name, created_at, images_dir, workspace, ply_path, mesh_path, status, n_images, elapsed_sec, error_msg`.

**server.py изменения:**
- `_state` расширен: `images_dir` (для OBJ-экспорта) и `scan_id` (FK в БД)
- При старте модуля: `init_db()` → `get_last_done_scan()` → если PLY на диске существует — восстанавливает состояние, разблокирует UI
- Тест-переопределение через `SCANNER_DB` env-var (установить до импорта)
- `scan_start`: создаёт запись `status=running`, передаёт `scan_id` в поток
- `_pipeline_thread`: обновляет запись на `done` (с `workspace, ply_path, mesh_path, elapsed_sec`) или `error`
- Новые эндпоинты: `GET /api/scans`, `POST /api/scans/{id}/load`, `DELETE /api/scans/{id}`

**Загрузка старого скана:** `POST /api/scans/{id}/load` → проверяет PLY на диске → обновляет `_state` → вьюер подгружает облако без пересчёта COLMAP.

**UI (История сканов):**
- Секция в левой панели, сворачивается кликом
- Кликабельные карточки (только `status=done`), активная карточка подсвечена
- При загрузке: автозаполняет `folderPath` (для OBJ-экспорта), вызывает `loadPLY`
- При старте страницы: восстанавливает состояние из `/api/status` автоматически

### Тесты

`python/tests/test_db.py` — 20 unit-тестов на чистый CRUD:
- init (idempotent), insert (returns id, default status), get (fields, nonexistent), update (done/error/noop), get_all (empty, DESC order), get_last_done (none, ignores errors, newest), delete

`python/tests/test_server_load.py` — 13 интеграционных тестов через `fastapi.testclient.TestClient`:
- `GET /api/scans`: пустой список, вставленный скан виден, порядок DESC
- `POST /api/scans/{id}/load`: 404 несуществующий, 400 неправильный статус, 404 PLY на диске нет, 200 успех + state обновлён + images_dir в ответе
- `DELETE /api/scans/{id}`: удаление, 404, не трогает другие записи

Результат: **33/33 passed** (0.7 сек).

`pip install httpx` добавлен в зависимости (нужен для TestClient).

### Следующие шаги

- **11.G pywebview** — нативное окно без браузера, `get_folder()` диалог
- **Финальное тестирование** — прогон с реальными фото, проверка полного UX

---

## 2026-05-13 — Десктоп приложение: FastAPI + Three.js UI (фазы 11.A–11.D)

### Что сделано

Начата реализация десктопного приложения. Пайплайн (C++/Python) готов, теперь интерфейс.
Стек: **FastAPI** (localhost:8765) + **Three.js r165** + **pywebview** (фаза 11.G, позже).

#### Фаза 11.A — FastAPI бэкенд (`python/api/server.py`, `python/api/run.py`)

- `POST /api/scan/start` — принимает путь к папке, запускает `ScanPipeline` в `daemon` потоке
- `GET /api/scan/stream` — SSE: шлёт `{step, progress, status}` каждые 0.5 сек; при `done` добавляет пути к PLY/mesh
- `GET /api/result/ply` — отдаёт `point_cloud_clean.ply`
- `GET /api/result/mesh` — отдаёт `mesh_repaired.ply` / `mesh_fixed.ply`
- `GET /api/status` — текущий state
- `StaticFiles` → `web/` на `/`; лог сервера в `data/results/server_{ts}.log`
- 409 если пайплайн уже запущен; `threading.Lock` для thread-safety

#### Фаза 11.B — Three.js UI (`web/`)

- `index.html`: layout flex — левая панель 280px + canvas справа; тёмная тема `#1a1a2e / #4fc3f7`
- `app.js`: кнопка выбора папки (pywebview API + fallback текстовый ввод), POST к API, SSE прогресс-бар + лог (5 строк), активация кнопок инструментов после `done`
- `viewer.js`: `PLYLoader` → `Points` с `VertexColors` или белый; `OrbitControls` с damping; мини-оси `AxesHelper` в нижнем левом углу (отдельная сцена 80×80 px); `loadPLY(url)` / `setMode(mode)`

#### Фаза 11.C — Orient (`viewer.js` + `server.py`)

- `TransformControls` (Three.js) прикрепляется к мешу; по умолчанию `rotate`
- Тулбар поверх вьюера: `[⟳ Rotate] [↔ Move] | [↺X] [↺Y] [↺Z] | [Авто] [Применить ✓]`
- Снапы `↺X/Y/Z` — `Quaternion.premultiply` на `PI/2` вокруг оси
- `[Применить]` → `mesh.matrix.elements` (16 float, column-major) → `POST /api/edit/apply-transform` → numpy трансформ вершин через trimesh → `mesh_oriented.ply`
- `POST /api/edit/auto-orient` → `PrintPreparation(mesh).auto_orient()` → `mesh_oriented.ply`
- `GET /api/result/oriented` → `mesh_oriented.ply` (fallback `mesh_repaired.ply`)
- `OrbitControls` отключается пока тащишь гизмо (`dragging-changed` event)

#### Фаза 11.D — Denoise (`viewer.js` + `server.py`)

- `Shift+drag` рисует прямоугольник (`#sel-rect`), на `mouseup`:
  - Проецирует все вершины в NDC через `projectionMatrix × matrixWorldInverse`
  - Проверяет попадание в прямоугольник → `selectedIndices[]`
- Выделенные точки → атрибут `color` = красный; повторные выделения накапливаются
- `[Удалить]` → `POST /api/edit/delete-points {indices}` → numpy mask на `pc.points/normals/colors` → `estimate_normals(k=30)` → сохраняет на место; `loadPLY` перезагружает облако
- `[Пересчитать меш]` → `POST /api/edit/remesh` → запускает `MeshProcessor.process_cloud` в thread → SSE прогресс через `CustomEvent('remesh-started')` в app.js
- `[Снять выделение]` → восстановить оригинальные цвета

### Архитектурные решения

- SSE (`text/event-stream`) вместо WebSocket — проще, достаточно для односторонних апдейтов
- Один `_state` dict с `threading.Lock` вместо `asyncio.Queue` — thread пишет, SSE читает
- Денойс использует ручной проецирование вершин вместо `SelectionBox` (он работает с объектами, не с отдельными точками)
- `CustomEvent('remesh-started')` для коммуникации между viewer.js и app.js без circular imports
- После `apply-transform` сервер применяет матрицу к вершинам и сбрасывает transform объекта в identity — пользователь видит «очищенный» гизмо

### Обновлён `scanner-guide-obsidian-v3.md`

Добавлена **Фаза 11** (7 промптов: A–G) в конец гайда — поэтапный план всего десктопного приложения с короткими копируемыми промптами в стиле предыдущих фаз.

### Следующие шаги (фазы 11.E–11.G)

- **11.E Repair** — подсветка открытых рёбер (`LineSegments` красным), `fill-holes`, `smooth`
- **11.F Export** — STL скачать, OBJ+texture ZIP через COLMAP `texture_mapper`
- **11.G pywebview** — нативное окно, `get_folder()` диалог, `run_desktop.ps1`

---

## 2026-05-12 — tst7 (кролик в саду), улучшения ground plane, старт UI

### tst7: кролик на пне в саду (222 фото, medium quality)

Самый сложный тест: объект на фоне травы, деревьев, неоднородного фона. Исходное
облако: 2 252 293 точки (fused.ply 58 MB, workspace `20260509_014144`).

**Основная проблема:** fused.ply включал газон, кусты, деревья → `remove_ground_plane` находил
вертикальные плоскости деревьев или горизонталь верхушки пня вместо реальной земли.

**Улучшения `_remove_ground_plane`:**

1. **PCA up-direction** — минимальный eigenvalue ковариационной матрицы = ось «вверх».
   Отклоняем кандидаты с нормалью < cos45° к up_dir (стены деревьев, вертикальный фон).
2. **Bottom-30% sampling** — RANSAC сэмплирует только нижние 30% точек по высоте.
   Предотвращает нахождение горизонтальных поверхностей объекта (верхушка пня, стол) как «земля».
3. **Minority_frac check** — если точек поровну с обеих сторон плоскости (>25/75 split),
   плоскость вертикальная → пропускаем. Горизонтальная земля: объект чётко с одной стороны.

**Результат tst7:** 2 252 293 → 880 019 точек; меш watertight, объём 764 174 mm³.
Чистый кролик без растительности. Лёгкий срез основания пня по линии земли — принято,
будет убрано вручную в desktop-редакторе.

**Исправленный баг:** `--dbscan-only-largest` устанавливал `fraction=0.0` (хранить все кластеры)
вместо `fraction=1.0` (только наибольший). Исправлено в `cli.py`.

**pymeshfix guard:** 25% → 40%. При крупных дырах (пространство между лапами) pymeshfix
добавлял >25% вершин и создавал фантомные «иглы». Guard повышен; случаи >40% пропускаются,
exporter закрывает через `cut_with_plane + add_flat_base`.

### Следующий шаг: Desktop 3D-редактор

Шаг 11 пайплайна — интерактивный редактор на **Three.js** (уже есть `web/`):
- **Align** — transform-гизмо для ручной ориентации модели по осям
- **Denoise** — выделение и удаление кластеров шума (лассо / bbox selection)
- **Base** — интерактивное размещение и настройка подставки

---

## 2026-05-08 — Фикс ground plane + ROR, тест tst4/tst1_video

### Проблема tst4: половина ракушки исчезала

**Диагноз:** два независимых бага:

1. **ROR слишком агрессивен на разреженных облаках.** tst4 low quality = 186K точек (vs 2.2M у tst5). `ror_radius = 0.2 * eps` стал слишком маленьким — у настоящих точек ракушки не хватало 6 соседей. ROR удалял 31% точек (58K!) легитимной геометрии.
   - **Фикс:** ROR пропускается если облако < 500K точек.

2. **Ground plane удалял дно объекта.** Старая логика: `keep = signed > threshold` — оставляла только то что СТРОГО выше плоскости. Ракушка лежит НА столе → её нижняя поверхность на уровне плоскости → удалялась. Из 127K точек оставалось 56K (55% потеря).
   - **Фикс:** новая логика — удалять только inlier-точки стола (`|signed| < threshold`) + явно ниже (`signed < -threshold*3`). Объект у основания сохраняется. Результат: 96K точек сохранено vs 56K раньше.

**Сравнение (tst4, fused.ply 186K точек):**
| Версия | После GP | Объём STL | Итог |
|---|---|---|---|
| v1 (старый) | 56 924 pts | — | половина ракушки срезана |
| v2 (без GP) | 185 914 pts | 138 млн mm³ | стол целиком в модели |
| v3 (новый GP) | 96 219 pts | 3 027 675 mm³ | ракушка полная, стол убран ✓ |

### Тест tst1_video

- Видео tst1.mp4 → VideoFrameExtractor: 125 кадров (sampled=533, sharp=322, unique=125)
- COLMAP sequential matcher: 111/125 изображений зарегистрировано
- Результат: watertight=True, bbox 250×333×99 мм, 10.7 мин
- Качество кадров видео неестественное (motion blur, ракурсы) → модель с зазорами. Для видео нужно снимать медленно и плавно.

### run_e2e_test.py — рефакторинг

- Добавлены tst6, tst7, tst1_video
- Per-test конфигурация: tst4 автоматически запускается с `remove_ground_plane=True`
- Поддержка видео-тестов (input из `data/test_videos/`)
- `process-cloud` CLI: добавлен флаг `--remove-ground-plane`

### Следующие шаги

1. Запустить tst6, tst7 (227 и 222 фото, exhaustive fallback)
2. Начать разработку десктоп 3D-редактора (Three.js: align/denoise/base)

---

## 2026-04-27 — Инициализация проекта

### Что сделано
- Создана полная структура директорий по CLAUDE.md
- `cpp/CMakeLists.txt`: `scanner_core` (STATIC) + `_scanner_cpp` (pybind11 .pyd)
- Скелеты C++ заголовков: `types.h`, `point_cloud.h`, `triangle_mesh.h`, `mesh_repair.h`, `print_preparation.h`
- Скелеты Python-модулей: `config.py`, `pipeline.py`, `video_extractor.py`, `colmap_runner.py`, `mesh_processor.py`, `exporter.py`, `cli.py`
- `python/pyproject.toml`: пакет `scanner`, build-backend `setuptools.build_meta`
- `.gitignore`, `.gitattributes` (LF для всего, CRLF для `.bat`/`.ps1`)
- `README.md` с инструкцией сборки

### Проблемы и решения
- `build-backend = "setuptools.backends.legacy:build"` → не поддерживается установленным setuptools; исправлено на `"setuptools.build_meta"`
- `open3d>=0.18` не поддерживает Python 3.13 → перенесён в `[project.optional-dependencies.mesh]`

---

## 2026-04-27 — Верификация C++ сборки

### Что сделано
- Минимальный `bindings.cpp`: только `hello()` → `"ok"` (pybind11)
- Минимальный `point_cloud.h`/`.cpp`: без nanoflann (stub имел `#error`)
- CMake configure + MSBuild → `_scanner_cpp.cp313-win_amd64.pyd`
- Добавлен `set(PYBIND11_FINDPYTHON ON)` → убраны CMake warnings C4148

```
python -c "import _scanner_cpp; print(_scanner_cpp.hello())"
# → ok
```

### Среда
- MSVC 19.44 (VS 2022), Windows 11, Python 3.13.3
- vcpkg: Eigen3 x64-windows
- pybind11 3.0.4 (pip install в venv)

---

## 2026-04-27 — types.h: MSVC-safe заголовок

### Изменения
| Проблема | Решение |
|----------|---------|
| Eigen → C4127 (conditional constant), C4714 (forceinline) | `#pragma warning(push/disable/pop)` вокруг `#include <Eigen/Dense>` |
| `enum class LogLevel { ..., ERROR }` — `ERROR` = макрос 0 в `<windows.h>` | Переименовано в `ERR` |
| `void log(...)` в header без `inline` → multiple definition | Добавлен `inline` |
| C4100 unreferenced parameter | `(void)level; (void)msg;` |

### triangle_mesh.h
- Удалены старые `Vec3f`, `Triangle` (из прежнего types.h)
- `std::vector<Vector3d>` для вершин и нормалей
- `using Triangle = std::array<uint32_t, 3>` внутри `namespace scanner`

**Сборка без warnings:** подтверждено MSBuild.

---

## 2026-04-27 — VideoFrameExtractor

### Реализация (python/scanner/video_extractor.py)
Алгоритм за один проход по видео:
1. Каждый `sample_every_n` кадр
2. Фильтр резкости: `Laplacian-variance > blur_threshold`
3. Фильтр уникальности: `min_diff < нормализованный MSE < max_diff`
   - MSE вычисляется на превью 320×180 (в 13× быстрее полного кадра)
   - Сравнение с последним **принятым** кадром
4. При `< min_frames` → повтор с порогами ×0.5 / ×1.5
5. При `> max_frames` → равномерное прореживание (`np.linspace`)

### Новые типы в config.py
- `VideoConfig` — изолированная конфигурация экстрактора
- `ExtractResult` — структурированный итог (paths, счётчики, флаги thinned/retried)

### CLI (python -m scanner extract-frames)
```
python -m scanner extract-frames video.mp4 -o .\frames\ --frames 300 --blur 100
```
- Добавлен `python/scanner/__main__.py` для `python -m scanner`
- CLI output — только ASCII (cp1251-safe, нет `→` U+2192)

### Тесты (python/tests/test_video_extractor.py)
13 тестов: helpers (`_sharpness`, `_mse`), happy path, именование, прореживание,
retry, несуществующий файл, создание директории, влияние `sample_every_n`.

```
13 passed in 3.92s
```

---

## 2026-04-27 — Демо экстрактора (experiments/demo_extractor.py)

### Видео: `data/test_videos/test3.mp4`
720×1280, 2095 кадров, 30 fps (~70 сек), ~26 MB

### ExtractResult
```
total_frames      = 2095
sampled_frames    = 1048   (retry: every_n=2 т.к. первый проход дал 1 кадр)
passed_sharpness  = 149    (14.2% — видео снято в движении)
passed_uniqueness = 19     (12.8% от резких)
saved             = 19
thinned           = False
retried           = True
```

### Выводы
- **Шарпнесс:** пик распределения — Laplacian var 10–15 (log-ось). blur_threshold=100
  стоит правее 97% кадров → видео снималось без стабилизации.
- **MSE:** все 698 пар — "too similar" (MSE < 0.03). При sample_every_n=3 на 30fps
  это 0.1 сек — камера почти не успевает переместиться.
- **Рекомендации для диплома:**
  - `blur_threshold = 30–50` для видео (100 — порог для фото)
  - Увеличить `sample_every_n` до 5–10 или использовать `min_difference = 0.005`

### Графики → `experiments/results/`
| Файл | Содержание |
|------|------------|
| `sharpness_hist.png` | Гистограмма Laplacian var по всем sampled кадрам (log-ось, порог отмечен) |
| `mse_hist.png` | Гистограмма нормализованного MSE (зоны: too similar / accepted / too different) |
| `pipeline_funnel.png` | Воронка 2095 → 1048 → 149 → 19 → 19 |
| `timeline.png` | Шарпнесс vs время видео (scatter, лог-ось Y) |

---

---

## 2026-04-27 — PointCloud C++ (шаг 2 пайплайна)

### Что сделано
- `cpp/include/scanner/point_cloud.h`: PIMPL-интерфейс (nanoflann скрыт от публичного API)
- `cpp/src/point_cloud.cpp`: полная реализация
- `cpp/third_party/nanoflann/nanoflann.hpp`: скачан v1.5.5 с GitHub (92 KB)

### PLY I/O
| Формат | Чтение | Запись |
|--------|--------|--------|
| ASCII | + | — |
| binary_little_endian | + | + |
| binary_big_endian | — | — |

Заголовок разбирается через property-map: поддержаны `x/y/z`, `nx/ny/nz`,
`red/green/blue` (`r/g/b`), все типы PLY (`float`, `double`, `uchar`, `int`, …).
Неизвестные свойства пропускаются. Записывает `float32` x,y,z,nx,ny,nz + `uint8` r,g,b.
Файлы открываются через `std::ifstream(path)` (C++17 — корректен с Unicode-путями на Windows).

### KD-tree (nanoflann)
- PIMPL: `PointCloudKDTreeImpl` полностью скрыт в `.cpp`
- `IndexType = std::size_t` (явно, иначе конфликт с дефолтным `uint32_t`)
- `k_nearest(q, k)` — knnSearch, результат уже отсортирован
- `radius_search(q, r)` — принимает r (не r²); nanoflann получает r² внутри
- После `center_to_origin()` kdtree_ инвалидируется (ссылка стала бы висячей)

### Исправленные ошибки компилятора
- C2664: `knnSearch` ожидал `uint32_t*`, передавался `size_t*` → задали `IndexType = std::size_t`

### Тест (ctest -C Release)
```
All tests PASSED   (1000 точек, 0.04 сек)
  BBox: [-9.98, -9.98, -9.99] - [9.98, 9.99, 9.92]
  KNN(42, k=5): [0(d²=0), 115(d²=3.79), 353(d²=3.83), 686(d²=4.26), 343(d²=5.51)]
  RadiusSearch(42, r=3): 14 points
```
10 проверок: size, save, load, round-trip XYZ/normals/colors, bounding_box, center_to_origin, KNN, radius.

---

---

## 2026-04-27 — PointCloud: SOR, Voxel Downsample, Estimate Normals

### Что сделано
- `statistical_outlier_removal(k=20, std_ratio=2.0) → PointCloud`
  - Для каждой точки: среднее расстояние до k-NN
  - Порог = global_mean + std_ratio × global_std
  - Точки выше порога = выбросы (удаляются)
- `voxel_downsample(voxel_size) → PointCloud`
  - Хэш-карта `unordered_map<VoxelKey, VoxelData>` (FNV-mix хэш для int64 i,j,k)
  - Центроид координат + средние нормали + средние цвета
- `estimate_normals(k=30)` — in-place, перезаписывает normals_
  - PCA через `Eigen::SelfAdjointEigenSolver<Matrix3d>` по ковариации окрестности
  - Ориентация: `if dot(normal, p - com) < 0 → flip`
- `ensure_kdtree()` — ленивое построение KD-tree (приватный метод, mutable unique_ptr)
- `k_nearest` / `radius_search` теперь используют `ensure_kdtree()` вместо throw

### Изменения заголовка
- `kdtree_` → `mutable std::unique_ptr<PointCloudKDTreeImpl>`
- Добавлен `void ensure_kdtree() const`

### Тест (ctest -C Release)
```
SOR: 5500 -> 5022 points    (сфера 5000 + шум 500 → удалено 478)
Voxel: 1000 -> 946 points
Normals aligned: 5000/5000  (100% правильно ориентированы)
All tests PASSED  (0.07 сек)
```

13 проверок: все предыдущие + SOR (size >= 4500, removed some noise), voxel (non-empty, reduced), normals (count == N, >= 90% aligned).

---

---

## 2026-04-27 — DBSCAN: segment_largest_cluster

### Что сделано
- `segment_largest_cluster(eps=0.02, min_points=50) → PointCloud`
  - BFS-DBSCAN через `radius_search(eps)` (nanoflann KD-tree)
  - Соседи помечаются id кластера при добавлении в очередь — дубликатов нет
  - Граничные точки (< min_points соседей) в кластер входят, расширение не запускают
  - Шум (label=-2) может быть поглощён соседним кластером при расширении

### Тест (два шара + шум)
```
total=2700 (2000 большой + 500 малый + 200 шум)
largest=2008  (expected ~2000)
All tests PASSED
```

---

## 2026-04-27 — Синтетический тест пайплайна (тор 30k + шум 5k)

### Что сделано
- `cpp/tests/demo_synthetic.cpp` — автономный C++ бинарник (не ctest)
- CMakeLists.txt: `add_executable(demo_synthetic ...)`
- Сохраняет `experiments/results/synthetic.ply` и `cleaned.ply`

### Параметры
- Тор: N=30000, R=2.0, r=0.8 (поверхность ~50.3 unit²)
- Шум: 5000 случайных точек в [-2.8, 2.8]³

### Результаты

| Шаг | Операция | Вход | Выход | Время |
|-----|----------|------|-------|-------|
| 1 | Generate | — | 35000 pts | 1.6 ms |
| 2 | Save PLY | — | 512 KB | 9.5 ms |
| 3 | Load PLY | — | 35000 pts | 15 ms |
| 4 | SOR(k=20, ratio=2.0) | 35000 | 31171 (-3829) | 87 ms |
| 5 | DBSCAN(eps=0.08, min=5) | 31171 | 30006 (-1165) | 39 ms |
| 6 | estimate_normals(k=20) | — | 30006 | 82 ms |
| 7 | Save cleaned.ply | — | 791 KB | 10 ms |

### Выводы
- SOR удалил 76.6% выбросов; DBSCAN доочистил оставшиеся
- Итого удалено 4994/5000 (99.9%) выбросов
- Сохранено 30006/30000 тора (6 шумовых точек случайно легли на поверхность)
- BBox: [-2.80, -2.80, -0.87] — [2.84, 2.80, 0.86] ✓ (ожидаемо: R+r=2.8 XY, r=0.8 Z)
- Полный пайплайн 35k точек: ~245 ms (без I/O: ~208 ms)

---

---

## 2026-04-29 — TriangleMesh: I/O, геометрия, топология

### Что сделано
- Полная переработка `cpp/include/scanner/triangle_mesh.h` (старый скелет — удалён)
- `cpp/src/triangle_mesh.cpp`: ~400 строк

#### Поля
| Поле | Тип | Описание |
|------|-----|---------|
| `vertices_` | `vector<Vector3d>` | XYZ вершины |
| `faces_` | `vector<Vector3i>` | Индексы вершин (int) |
| `normals_` | `vector<Vector3d>` | Per-face нормали |
| `colors_` | `vector<Color>` | Per-vertex RGB |

#### I/O
| Метод | Формат | Особенности |
|-------|--------|-------------|
| `load_ply` | binary LE + ASCII | property-map; list uchar int для граней |
| `save_ply` | binary LE | vertex + face элементы |
| `load_stl` | binary | дедупликация вершин через `unordered_map<float3>` |
| `save_stl` | binary | 80B header + 50B/треугольник |
| `save_obj` | ASCII | `v`, `vn`, `f v//n` |

#### Геометрия и топология
- `compute_normals()` — per-face через векторное произведение
- `surface_area()` — сумма площадей треугольников
- `volume()` — через теорему Гаусса: `|Σ v0·(v1×v2)| / 6`
- `is_watertight()` — каждое ребро ровно в 2 гранях
- `build_edge_map()` — `map<pair<int,int>, vector<int>>` (key: min < max)
- `find_boundary_edges()` — рёбра с count ≠ 2
- `get_vertex_neighbors(v)` — обход граней, set соседей

#### Рефакторинг
- PLY-хелперы (`PropType`, `str_to_proptype`, `read_bin_double`) вынесены в `cpp/src/ply_io.h`
- `point_cloud.cpp` обновлён — включает `ply_io.h` вместо локальных определений

### Тест (ctest -C Release) — единичный куб
```
surface_area = 6.0  ✓
volume = 1.0        ✓
is_watertight = true ✓
build_edge_map: 18 рёбер, все в ровно 2 гранях
neighbors(0): {1,2,3,4,5,7}  (6 соседей угловой вершины)
удалили 1 грань → 3 граничных ребра
STL round-trip: 8 вершин, 12 граней (дедупликация сработала)
PLY round-trip: 8 вершин, 12 граней
OBJ: 472 байта
All tests PASSED  (0.03 сек)
```

---

## 2026-04-29 — MeshRepair: 6 операций + RepairReport

### Что сделано
- `cpp/include/scanner/mesh_repair.h` — класс `MeshRepair(TriangleMesh&)` + `RepairReport`
- `cpp/src/mesh_repair.cpp`: ~300 строк

#### Методы

| Метод | Алгоритм | Возвращает |
|-------|----------|-----------|
| `remove_degenerate_faces()` | дублированные индексы или площадь² < 1e-24 | count |
| `remove_duplicate_faces()` | сортировка 3 индексов → `set<tuple>` | count |
| `merge_close_vertices(thr)` | x-сортировка + скользящее окно + union-find | count |
| `make_manifold()` | `build_edge_map()`, удалить грани с ребром в > 2 гранях | count |
| `fill_holes(max)` | трассировка граничных полурёбер → фановая триангуляция | count |
| `laplacian_smooth(iter, λ)` | Лаплас по рёбрам, граничные вершины не двигать | void |
| `repair_all(smooth_iter)` | полный цикл, возвращает `RepairReport` | struct |

#### fill_holes — ключевой инвариант
Граничный контур идёт по **отсутствующим** направленным рёбрам:
для ребра `(a→b)` в грани без обратного `(b→a)` — отсутствует `(b→a)`,
поэтому `boundary_next[b] = a` (а не `[a] = b`).
Ошибка в направлении делала грани с инвертированными нормалями → объём ≠ 1.0.

### Тест (ctest -C Release)
```
boundary edges: 4       (куб без 2 треугольников правой грани)
filled=1  faces=12  watertight=1
degenerate removed: 2
duplicates removed: 2
vertices merged: 1      (вершина на расстоянии 1e-8 < 1e-6)
smooth: vol 1 -> 0.000286  (замкнутый куб без граничных вершин — все двигаются)
repair_all: degenerate=1  dup=1  merged=0  holes=1
All tests PASSED  (0.01 сек)
```

**Статус тестов:**
```
1/3 test_point_cloud   PASSED  0.04 s
2/3 test_triangle_mesh PASSED  0.01 s
3/3 test_mesh_repair   PASSED  0.01 s
100% tests passed
```

---

## 2026-04-30 — PrintPreparation C++ (шаг 9 пайплайна)

### Что сделано
- `cpp/include/scanner/print_preparation.h` — полная замена скелета
- `cpp/src/print_preparation.cpp` — полная реализация
- `cpp/tests/test_print_preparation.cpp` — 7 тестов
- Добавлен в `CMakeLists.txt` + `ctest`

### API

| Метод | Описание |
|-------|----------|
| `cut_with_plane(point, normal)` | Sutherland-Hodgman обрезка; граница остаётся открытой для `add_flat_base` |
| `add_flat_base(thickness=2.0)` | Трассировка граничного контура → боковые стенки + нижняя крышка |
| `scale_to_size(target_mm, axis)` | Равномерный масштаб до целевого размера вдоль оси |
| `auto_orient()` | Грань с max площадью → вниз (`AngleAxisd`), z_min → 0 |
| `check_printability()` | `PrintabilityReport`: watertight, thin_walls (<0.4 мм), overhangs (>45°), bbox, volume |

### Алгоритм `cut_with_plane`

Sutherland-Hodgman клиппинг:
- `dist[v] = n·(v−p)`: ≤0 = ниже (оставить), >0 = выше (отрезать)
- `split_edge(a,b)`: если dist[b]≈0 — вернуть b напрямую (не создавать дубликат на плоскости!)
- `cnt=1` (1 ниже): `{va, pab, pac}`
- `cnt=2` (2 ниже): `{vb, vc, pac}` + `{vb, pac, pab}`
- Порядок после клиппинга: `remove_degenerate_faces` → compact vertices → (граница открыта для `add_flat_base`)

**Критический инвариант `split_edge`:** если конечная точка ребра лежит на плоскости (dist≈0),
возвращать её индекс напрямую. Иначе создаётся дубликат вершины с другим индексом,
который добавляет ложные рёбра `0→P1` в de_set и нарушает трассировку граничного контура.

**Порядок после клиппинга (критически важен):**
1. `remove_degenerate_faces` — убрать `{v, P, v}` и т.п. (иначе de_set получает ложные рёбра)
2. compact vertices — убрать вершины без ссылок (срезанная часть)
3. граница остаётся открытой — `add_flat_base` закроет её

### Алгоритм `add_flat_base`

Та же трассировка граничного контура, что в `fill_holes` (directed half-edges):
- `z_base = z_min − thickness`
- Боковые стенки: `{top_j, top_i, bot_i}`, `{top_j, bot_i, bot_j}` (нормали наружу)
- Нижняя крышка: `{cen_idx, base[i], base[(i+1)%n]}` (нормаль −Z)

### Исправленные ошибки
| Ошибка | Причина | Исправление |
|--------|---------|-------------|
| `cut_with_plane: no vertex above plane` | vertex compaction после fill_holes не убирал вершины | убрать `fill_holes` из cut; compact делать до fill |
| `cut: watertight after cut` | fill_holes закрывал дырку — add_flat_base не находил границу | cut оставляет открытую границу; fill делает add_flat_base |
| `add_flat_base: face count` | mesh уже watertight, boundary_next пуст | исправлено предыдущим пунктом |
| `pipeline: watertight after cut` | тест проверял watertight до add_flat_base | тест исправлен: after cut = open |
| Дублирующие вершины на плоскости | split_edge не возвращал оригинальный vertex при dist≈0 | added early-return: `if (abs(dist[b]) < 1e-12) return b` |
| fill_holes видел ложные boundary edges | degenerate faces `{0,P1,0}` добавляли `0→P1` в de_set | remove_degenerate_faces до compact и fill |

### Тест (ctest -C Release)
```
icosphere: surface=9.57  vol=2.54
after cut: faces=12  boundary=6
after base: faces=30  watertight=1
after scale: z-height=50
auto_orient: z_min=0
pipeline: vol=48682 mm3  sa=11608 mm2  warnings=1
STL saved: test_printprep.stl
cube: vol=1  sa=6  warnings=1
All tests PASSED  (0.01 сек)
```

Python trimesh: `watertight: True  volume: 92452.9 mm3  faces: 54`

**Статус тестов:**
```
1/4 test_point_cloud       PASSED  0.06 s
2/4 test_triangle_mesh     PASSED  0.01 s
3/4 test_mesh_repair       PASSED  0.01 s
4/4 test_print_preparation PASSED  0.01 s
100% tests passed
```

---

## Следующий шаг: Python-биндинги (_scanner_cpp.pyd) — pybind11 обёртка для C++ ядра

---

## 2026-05-04 — Многокластерный DBSCAN + подставка-диск + фикс среза

### Контекст
Тестовый датасет tst4: аммонит (ракушка) на металлическом болте. 102 фотографии.
С каждым изменением результат STL менялся — добавлен git для возможности отката.

### Изменения

#### 1. `remove_ground_plane` — обязательно для tst4
- fused.ply содержит ~58.5% точек стола (тёмно-коричневая поверхность)
- Без RANSAC-удаления стола DBSCAN включает части стола в результат
- Флаг `remove_ground_plane=True` нужен для любого объекта НА столе
- В config.py дефолт: `remove_ground_plane=False` (не менять — ломает случаи без стола)
- **Для e2e теста с tst4: запускать с `--remove-ground-plane`**

#### 2. Многокластерный DBSCAN (`dbscan_min_cluster_fraction=0.05`)
- Старый вариант: DBSCAN оставлял ТОЛЬКО наибольший кластер
- Проблема: внутренняя спираль аммонита (вогнутая) → отдельный кластер → удалялась
- Новый: сохранять все кластеры >= 5% от наибольшего
- Результат: внутренняя спираль сохранена, DBSCAN 99.6% retention (было 57%)
- **Внимание:** если стол не убран, 5%-порог сохраняет куски стола → огромный bbox!
  Поэтому remove_ground_plane=True должен идти ПЕРЕД DBSCAN

#### 3. Подставка-диск вместо среза (`add_disc_stand`)
- Старый вариант: `cut_with_plane` + `add_flat_base` — срезал геометрию объекта
- Проблема A: срез делал видимый плоский разрез на ракушке
- Проблема B: если Z-высота < 0.1 COLMAP-единиц → cut_z > z_max → меш уничтожался целиком
- Новый: если меш watertight → `add_disc_stand` (круглая подставка снизу, радиус = 90% min_bbox_xy/2)
- Новый: если есть дыры → `add_flat_base` (без среза, только закрытие дыр)
- `add_disc_stand` добавляет 64-угольный цилиндр высотой `base_thickness_mm` под объект

#### 4. Параметры (config.py)
| Параметр | Старое | Новое | Причина |
|----------|--------|-------|---------|
| `outlier_std` | 2.0 | 3.0 | Сохранить разреженные точки в вогнутых зонах |
| `dbscan_eps_factor` | 3.0 | 4.0 | Соединять точки через зазоры (вогнутые поверхности) |
| `dbscan_min_cluster_fraction` | — | 0.05 | Новый параметр: сохранять кластеры >= 5% наибольшего |
| `stand_radius_fraction` | — | 0.9 | Радиус подставки = 90% от min(bbox_x, bbox_y)/2 |

### Результат tst4 с `remove_ground_plane=True`
```
Ground plane: inliers=58.5%, removed=268550 pts
DBSCAN: 190576 -> 189858 pts (99.6% kept)
pymeshfix: 362728->387634 verts, watertight=True
add_disc_stand: r=90% bbox_min
bbox=49.0x35.7x100.0 mm  vol=76958mm3
watertight=True  open_edges=0
```

### Известные проблемы / Следующий шаг
1. Внутренняя спираль аммонита: точки в центре всё ещё не полностью (COLMAP не снимает внутрь глубоких полостей — ограничение фотограмметрии, не кода)
2. Нужен полный e2e-тест с 200 фотографиями (`run_e2e_test.py tst4 --remove-ground-plane`)
3. Проверить STL в слайсере (PrusaSlicer) — убедиться что подставка-диск нормального размера
4. vocab_tree для COLMAP (>200 фото) пока не скачан → matcher=exhaustive (медленно)
