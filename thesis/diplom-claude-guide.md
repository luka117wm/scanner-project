# Руководство по написанию ВКР с помощью Claude

**Тема:** Разработка фрагментов программы построения трехмерных объектов по двумерным изображениям

---

## ⚠️ ПРАВИЛА ОФОРМЛЕНИЯ

> **ВАЖНО:** Перед каждым сеансом работы с Claude прикрепи к диалогу PDF/DOCX с требованиями
> оформления своего вуза. В начале промпта пиши:
>
> _«Правила оформления прикреплены. Строго соблюдай: шрифт, отступы, нумерацию, оформление
> рисунков/таблиц/формул/списка литературы — всё по прикреплённому документу.»_

Типичные требования (уточни по своему вузу):
- Шрифт: Times New Roman 14 пт, межстрочный интервал 1,5
- Поля: левое 30 мм, правое 15 мм, верхнее/нижнее 20 мм
- Нумерация страниц: внизу по центру, начиная с введения
- Рисунки: «Рисунок N — Название», по центру под рисунком
- Таблицы: «Таблица N — Название», над таблицей слева
- Формулы: по центру с номером в скобках справа
- Список литературы: ГОСТ Р 7.0.5-2008

---

## Структура отчёта и порядок работы

Пиши отчёт **по главам**, каждую главу в отдельном сеансе. Не пытайся написать всё сразу.

```
Введение          → ~2-3 стр
Глава 1           → ~15-20 стр  (обзор и теория)
Глава 2           → ~20-25 стр  (проектирование)
Глава 3           → ~15-20 стр  (реализация)
Глава 4           → ~10-15 стр  (эксперименты)
Заключение        → ~2-3 стр
Список литературы → ~2-3 стр
Приложения        → код, схемы
```

---

## Введение

### Что должно быть

- Актуальность задачи построения 3D-моделей по фотографиям
- Цель работы: разработка программных фрагментов системы фотограмметрической реконструкции
- Задачи: анализ методов, реализация алгоритмов, экспериментальное исследование
- Объект исследования: методы Structure-from-Motion и мультивидовой стереореконструкции
- Предмет исследования: алгоритмы обработки облаков точек и построения полигональных сеток
- Практическая значимость
- Структура работы (краткое описание каждой главы)

### Промпт для Claude

```
[Прикрепи правила оформления]

Напиши Введение к ВКР на тему:
«Разработка фрагментов программы построения трехмерных объектов по двумерным изображениям»

Цель: разработать программные компоненты системы, которая по набору фотографий одного
объекта восстанавливает его трёхмерную геометрию в виде полигональной сетки.

Задачи:
1. Анализ методов фотограмметрической реконструкции (SfM, MVS)
2. Разработка C++-ядра: облако точек (загрузка PLY, статистический выброс, DBSCAN,
   оценка нормалей) и полигональная сетка (ремонт дефектов — дырки, дублирующиеся
   грани, невалидные рёбра)
3. Разработка Python-пайплайна: оркестрация COLMAP, Poisson-реконструкция, интеграция
   C++-модуля через pybind11
4. Разработка REST API и интерактивного веб-интерфейса визуализации
5. Экспериментальное исследование влияния параметров (количество фотографий,
   глубина Poisson, пороги фильтрации) на качество реконструкции

Объект: методы и алгоритмы фотограмметрической реконструкции трёхмерных объектов.
Предмет: программные фрагменты системы обработки облаков точек и построения меша.

Используй нейтральный академический стиль. Не упоминай 3D-печать.
Объём ~2-3 страницы.
```

---

## Глава 1. Анализ предметной области и методов реконструкции

### Что должно быть

1.1 Задача фотограмметрической реконструкции  
1.2 Метод Structure-from-Motion (SfM)  
— SIFT-дескрипторы (Lowe, 2004), сопоставление, Bundle Adjustment  
— Результат: разреженное облако + позиции камер  

1.3 Мультивидовая стереореконструкция (MVS)  
— PatchMatch Stereo, карты глубины, fusion  
— Результат: плотное облако (dense fused.ply)  

1.4 Алгоритмы обработки облаков точек  
— Statistical Outlier Removal (SOR)  
— Radius Outlier Removal (ROR)  
— Алгоритм DBSCAN (кластеризация)  
— Оценка нормалей методом PCA  

1.5 Методы построения полигональной сетки  
— Poisson Surface Reconstruction (Kazhdan et al., 2013)  
— Сравнение с Ball-Pivoting, Marching Cubes  

1.6 Ремонт меша  
— Типы дефектов: дублирующиеся грани, вырожденные треугольники, невалидные рёбра, дыры  
— Алгоритмы: fan-triangulation для закрытия дыр, Laplacian smoothing  

1.7 Существующие решения и обоснование выбора стека  
— COLMAP (Schönberger & Frahm, 2016): открытый, лучший на бенчмарках  
— Open3D: Poisson из Python  
— Собственное C++ ядро: контроль над алгоритмами фильтрации  

### Промпт для Claude

```
[Прикрепи правила оформления]

Напиши Главу 1 ВКР «Анализ предметной области и методов реконструкции».

Тема работы: «Разработка фрагментов программы построения трехмерных объектов
по двумерным изображениям».

Разделы главы:
1.1 — Постановка задачи трёхмерной реконструкции по фотографиям
1.2 — Structure-from-Motion: SIFT-дескрипторы, сопоставление особых точек,
      Bundle Adjustment, результат — разреженное облако точек
1.3 — Мультивидовая стереореконструкция: PatchMatch Stereo, карты глубины,
      слияние в плотное облако (dense fusion)
1.4 — Алгоритмы обработки облаков точек: Statistical Outlier Removal,
      Radius Outlier Removal, DBSCAN-кластеризация, оценка нормалей (PCA)
1.5 — Методы триангуляции: Screened Poisson Surface Reconstruction,
      сравнение с Ball-Pivoting и Marching Cubes
1.6 — Алгоритмы ремонта полигональных сеток: типы дефектов,
      fan-triangulation для дыр, Laplacian smoothing
1.7 — Обзор существующих инструментов (COLMAP, Open3D, trimesh, pymeshfix),
      обоснование выбора

Список литературы в конце главы (ГОСТ Р 7.0.5-2008):
— Schönberger, Frahm — Structure-from-Motion Revisited, CVPR 2016
— Schönberger et al — Pixelwise View Selection for MVS, ECCV 2016
— Kazhdan, Hoppe — Screened Poisson Surface Reconstruction, ACM TOG 2013
— Lowe — Distinctive Image Features from Scale-Invariant Keypoints, IJCV 2004
— Bernardini et al — Ball-Pivoting Algorithm, IEEE TVCG 1999
— Hartley, Zisserman — Multiple View Geometry in Computer Vision, 2003

Не упоминай 3D-печать. Академический стиль. Формулы нумеруй. ~20 страниц.
```

---

## Глава 2. Проектирование программного комплекса

### Что должно быть

2.1 Общая архитектура системы  
— 4-уровневая: входные данные → пайплайн → API → интерфейс  
— Схема: фотографии → COLMAP (SfM+MVS) → C++ ядро → Python → веб-вьюер  

2.2 Разработка C++ ядра (_scanner_cpp.pyd)  
— Класс PointCloud: хранение, PLY I/O, KD-tree (nanoflann), алгоритмы фильтрации  
— Класс TriangleMesh: хранение, PLY/STL/OBJ I/O, топологические операции  
— Класс MeshRepair: 6 операций ремонта, RepairReport  
— Интеграция с Python через pybind11  

2.3 Пайплайн обработки (10 шагов)  
— Шаг 0: VideoFrameExtractor (если вход — видео)  
— Шаг 1: COLMAP (feature_extractor → matcher → mapper → stereo_fusion)  
— Шаги 2–4: обработка облака (SOR, ROR, DBSCAN, downsample, нормали)  
— Шаг 5: Poisson meshing (Open3D, depth=9 по умолчанию)  
— Шаги 6–8: ремонт меша (degenerate, merge, manifold, holes, smooth)  
— Шаг 9: авто-ориентация и экспорт  

2.4 REST API (FastAPI)  
— Эндпоинты, SSE-прогресс, SQLite история сканов  
— Thread-safety: threading.Lock, daemon-потоки  

2.5 Веб-интерфейс (Three.js)  
— PLY-визуализация облака и меша  
— Инструменты постобработки: Orient (TransformControls), Denoise (bbox-выделение), Repair  

2.6 Выбор технологий и обоснование  
— C++17 + MSVC: производительность, Windows-совместимость  
— Python 3.11 + FastAPI: быстрая разработка API, asyncio  
— pybind11: zero-overhead биндинги C++ → Python  
— nanoflann: header-only KD-tree без внешних зависимостей  
— Three.js: 3D в браузере без установки  

### Промпт для Claude

```
[Прикрепи правила оформления]

Напиши Главу 2 ВКР «Проектирование программного комплекса».

Тема: «Разработка фрагментов программы построения трёхмерных объектов
по двумерным изображениям».

Реализованная система имеет следующую архитектуру:

ВХОДНЫЕ ДАННЫЕ → COLMAP (SfM + MVS) → C++ ядро → Python-пайплайн → FastAPI → Three.js

C++ ядро (компилируется как _scanner_cpp.pyd через pybind11):
- PointCloud: загрузка/сохранение PLY (binary LE + ASCII), KD-tree на nanoflann,
  методы: statistical_outlier_removal(k=20, std_ratio), radius_outlier_removal(r, min_nb),
  voxel_downsample(voxel_size), segment_largest_cluster (DBSCAN через BFS),
  estimate_normals (PCA + ориентация от CoM)
- TriangleMesh: PLY/STL/OBJ I/O, compute_normals, surface_area, volume, is_watertight,
  build_edge_map, find_boundary_edges
- MeshRepair: remove_degenerate_faces, remove_duplicate_faces, merge_close_vertices,
  make_manifold, fill_holes (fan-triangulation), laplacian_smooth, repair_all

Пайплайн (10 шагов):
Шаг 0: VideoFrameExtractor — Laplacian резкость + MSE уникальность → 200–500 JPEG
Шаг 1: COLMAP — feature_extractor (SIFT, GPU) → exhaustive/vocab_tree/sequential matcher →
        mapper (Bundle Adjustment) → image_undistorter → patch_match_stereo → stereo_fusion
        → fused.ply (dense point cloud)
Шаги 2–4: SOR → ROR (только для >500K точек) → DBSCAN → voxel_downsample → нормали
Шаг 5: Open3D Poisson (depth=7/9/11 в зависимости от quality preset)
Шаги 6–8: MeshRepair.repair_all() → pymeshfix (дополнительный ремонт)
Шаг 9: авто-ориентация (крупнейшая грань вниз) → экспорт PLY/OBJ

REST API (FastAPI, порт 8765):
- POST /api/scan/start — запуск в daemon-thread, параметр quality (low/medium/high)
- GET /api/scan/stream — SSE прогресс каждые 0.5 сек
- GET /api/result/ply, /api/result/mesh, /api/result/oriented
- POST /api/edit/delete-points, /api/edit/remesh, /api/edit/apply-transform,
  /api/edit/fill-holes, /api/edit/smooth
- GET /api/scans, POST /api/scans/{id}/load — SQLite история
- GET /api/export/download/stl, /api/export/download/obj

Веб-интерфейс (Three.js r165, вендоринг):
- PLYLoader: Points (VertexColors) + Mesh (MeshStandardMaterial)
- OrbitControls с damping
- TransformControls для ориентации (режим orient)
- bbox-выделение точек Shift+drag (режим denoise)
- 2D Canvas для отображения осей (axes overlay)

Нарисуй UML/блок-схемы где нужно (опиши словами, я вставлю рисунки).
Не упоминай 3D-печать. ~20 страниц.
```

---

## Глава 3. Реализация ключевых алгоритмов

### Что должно быть

3.1 Реализация KD-tree и алгоритмов поиска соседей (nanoflann)  
3.2 Statistical Outlier Removal — формулы, код, тест  
3.3 Алгоритм DBSCAN через BFS + radius_search  
3.4 Оценка нормалей: PCA через Eigen::SelfAdjointEigenSolver  
3.5 Poisson Surface Reconstruction через Open3D  
3.6 Закрытие дыр: трассировка граничного контура + fan-triangulation  
3.7 Laplacian smoothing: формула, граничные вершины фиксированы  
3.8 Интеграция с COLMAP: subprocess, авто-выбор matcher  
3.9 Привязка C++ → Python через pybind11 (фрагменты bindings.cpp)  
3.10 Десктопный интерфейс: SSE-прогресс, bbox-выделение точек, сохранение трансформации  

### Промпт для Claude

```
[Прикрепи правила оформления]

Напиши Главу 3 ВКР «Реализация ключевых алгоритмов».

Для каждого алгоритма: словесное описание → формулы → фрагмент кода (C++ или Python)
→ результат на тестовых данных.

Алгоритмы для описания:

1. Statistical Outlier Removal (cpp/src/point_cloud.cpp):
   Для каждой точки i: d̄ᵢ = среднее расстояние до k ближайших соседей.
   Глобальный порог: μ + std_ratio·σ. Точки с d̄ᵢ > порога удаляются.
   Реализация: KD-tree knnSearch, Eigen для статистики.
   Тест: сфера 5000 + 500 шум → после SOR: 5022 точки, удалено 478 выбросов.

2. DBSCAN через BFS (cpp/src/point_cloud.cpp):
   BFS-обход: для каждой непомеченной точки radius_search(eps).
   Граничные точки (соседей < min_points) входят в кластер, но не расширяют его.
   Метка шума = -2. Сохраняются все кластеры >= min_cluster_fraction от наибольшего.
   Тест: два шара + 200 шум → largest cluster = большой шар.

3. Оценка нормалей через PCA (cpp/src/point_cloud.cpp):
   Ковариационная матрица 3×3 по k-окрестности.
   Eigen::SelfAdjointEigenSolver → наименьший eigenvalue → нормаль.
   Ориентация: dot(normal, p - CoM) < 0 → flip.

4. Закрытие дыр fan-triangulation (cpp/src/mesh_repair.cpp):
   Граничный контур: для ребра (a→b) в грани без обратного (b→a):
   boundary_next[b] = a. Трассировка: пройти контур → центроид → fan грани.
   Порядок: (centroid, boundary[i], boundary[i+1]) с нормалью внутрь.

5. Поиск интегрирования COLMAP (python/scanner/colmap_runner.py):
   subprocess.run([str(colmap_bat), cmd, ...], shell=False, check=True).
   Авто-выбор matcher: exhaustive (<200 фото), vocab_tree (>200), sequential (видео).
   Quality profiles: low/medium/high → max_image_size, max_num_features,
   geom_consistency.

6. pybind11 биндинг (cpp/python/bindings.cpp):
   Показать как PointCloud и MeshRepair экспортируются в Python с numpy.

Код давай в листингах с нумерацией. Формулы нумеруй. ~15 страниц.
```

---

## Глава 4. Экспериментальное исследование

### Что должно быть

4.1 Описание методики и тестовых объектов  
4.2 Эксперимент 1: влияние числа фотографий на качество реконструкции  
4.3 Эксперимент 2: влияние глубины Poisson (depth 7 / 9 / 11)  
4.4 Эксперимент 3: качество фильтрации облака (с SOR+ROR+DBSCAN / без)  
4.5 Эксперимент 4: видео против фотографий  
4.6 Сводная таблица результатов  
4.7 Выводы по экспериментам  

### Данные из реальных тестов (подставь свои цифры)

| Тест | Объект | Фото | Время COLMAP | Точек fused.ply | После фильтрации |
|------|--------|------|--------------|-----------------|-----------------|
| tst4 | Ракушка (аммонит) | 102 | ~15 мин | 186 000 | 96 219 |
| tst5 | Объект на улице | 200 | 2.4 мин (exhaustive) | 2 195 752 | ~880 000 |
| tst7 | Кролик в саду | 222 | ~80-90 мин (medium) | 2 252 293 | 880 019 |
| tst1_video | Объект (видео) | 125 кадров | 10.7 мин | — | watertight ✓ |

### Промпт для Claude

```
[Прикрепи правила оформления]

Напиши Главу 4 ВКР «Экспериментальное исследование».

Тема: «Разработка фрагментов программы построения трёхмерных объектов
по двумерным изображениям».

Методика: запуск системы на реальных фотоданных с измерением:
- числа зарегистрированных изображений COLMAP
- плотности облака точек (число вершин dense fused.ply)
- числа точек после фильтрации (SOR + ROR + DBSCAN)
- числа граней итоговой сетки
- наличия дефектов (watertight, open_edges, volume мм³)
- времени обработки

Тестовые объекты:
[Опиши свои объекты: материал, форма, условия съёмки]

Эксперимент 1 — влияние числа фотографий (20 / 40 / 80 / 120 / 200 / 220):
[Вставь свои данные из experiments/results/]

Эксперимент 2 — глубина Poisson (depth=7 / 9 / 11):
[Сравни: число граней, захваченная деталь, время меша]

Эксперимент 3 — эффективность фильтрации:
Данные из реальных тестов:
- tst5 (200 фото, улица): fused.ply 2 195 752 точки →
  ROR (factor=0.2): удалено 157 222 (7.2%) →
  DBSCAN: итог ~880 000 точек
- tst7 (222 фото, кролик в саду): 2 252 293 → 880 019 точек,
  Ground-plane removal: удалено 58.5% фона (газон, деревья)
- tst4 (102 фото, ракушка на столе): 186 000 → 96 219 точек,
  без ROR (облако < 500K) — только SOR + ground_plane + DBSCAN

Эксперимент 4 — видео vs фото:
- tst1_video: 125 кадров извлечено (из 2095, retried — первый проход дал 1 кадр),
  COLMAP sequential matcher: 111/125 зарегистрировано, 10.7 мин, watertight=True
- Вывод: видео даёт motion blur, нужна медленная плавная съёмка

Для каждого эксперимента: таблица + график (опиши содержание, я вставлю рисунки).
Академический стиль. Не упоминай 3D-печать. ~12 страниц.
```

---

## Заключение

### Промпт для Claude

```
[Прикрепи правила оформления]

Напиши Заключение к ВКР.

Тема: «Разработка фрагментов программы построения трёхмерных объектов
по двумерным изображениям».

Что реализовано:
1. C++ ядро (_scanner_cpp.pyd): классы PointCloud, TriangleMesh, MeshRepair
   с алгоритмами SOR, ROR, DBSCAN, PCA-нормали, fill_holes, laplacian_smooth
2. Python-пайплайн: 10-шаговая обработка фото/видео → полигональная сетка,
   интеграция COLMAP через subprocess, Open3D Poisson, pybind11
3. REST API (FastAPI): управление пайплайном, SSE-прогресс, история сканов (SQLite)
4. Веб-интерфейс (Three.js): визуализация облака и меша, инструменты
   постобработки (ориентация, удаление шума, ремонт меша)
5. Экспериментальное исследование: [кратко итоги своих экспериментов]

Что получилось по экспериментам:
- [вставь свои главные выводы]

Направления дальнейшего развития:
- Использование нейросетевых методов реконструкции (NeRF, 3D Gaussian Splatting)
- Поддержка видео в реальном времени
- Оптимизация DBSCAN для GPU (CUDA)

Объём ~2 страницы. Академический стиль.
```

---

## Список литературы

Вставь в конец итогового документа:

```
1. Schönberger J. L., Frahm J.-M. Structure-from-Motion Revisited //
   Proceedings of the IEEE CVPR. — 2016. — С. 4104–4113.

2. Schönberger J. L. et al. Pixelwise View Selection for Unstructured Multi-View
   Stereo Rendering // ECCV. — 2016. — С. 501–518.

3. Kazhdan M., Hoppe H. Screened Poisson Surface Reconstruction //
   ACM Transactions on Graphics. — 2013. — Т. 32, № 3. — С. 1–13.

4. Lowe D. G. Distinctive Image Features from Scale-Invariant Keypoints //
   International Journal of Computer Vision. — 2004. — Т. 60, № 2. — С. 91–110.

5. Bernardini F. et al. The Ball-Pivoting Algorithm for Surface Reconstruction //
   IEEE Transactions on Visualization and Computer Graphics. — 1999. —
   Т. 5, № 4. — С. 349–359.

6. Hartley R., Zisserman A. Multiple View Geometry in Computer Vision. —
   2nd ed. — Cambridge : Cambridge University Press, 2003. — 655 с.

7. Ester M. et al. A Density-based Algorithm for Discovering Clusters in Large
   Spatial Databases with Noise // KDD-96. — 1996. — С. 226–231.

8. Attene M. et al. Polygon Mesh Repairing: An Application Perspective //
   ACM Computing Surveys. — 2013. — Т. 45, № 2.

9. Özyeşil O. et al. A Survey of Structure from Motion // Acta Numerica. —
   2017. — Т. 26. — С. 305–364.

10. Jakob W. et al. pybind11 — Seamless operability between C++11 and Python
    [Электронный ресурс]. — 2017. — URL: https://github.com/pybind/pybind11

11. Zhou Q.-Y. et al. Open3D: A Modern Library for 3D Data Processing //
    arXiv:1801.09847. — 2018.

12. Blanco J. L., Rai P. K. nanoflann: a C++11 Header-Only Fork of FLANN
    [Электронный ресурс]. — 2014. — URL: https://github.com/jlblancoc/nanoflann
```

---

## Приложения

**Приложение А** — Листинг `cpp/src/point_cloud.cpp` (полностью или ключевые методы)  
**Приложение Б** — Листинг `cpp/src/mesh_repair.cpp`  
**Приложение В** — Листинг `python/scanner/pipeline.py`  
**Приложение Г** — Листинг `cpp/python/bindings.cpp`  
**Приложение Д** — Скриншоты интерфейса  

### Промпт для приложений

```
[Прикрепи правила оформления]

Оформи Приложение А «Листинг модуля обработки облака точек».

Файл: cpp/src/point_cloud.cpp
[Вставь содержимое файла]

Оформи по требованиям: шрифт Courier New 10/12 пт, одинарный интервал,
нумерация строк. Заголовок: «Приложение А. Листинг программного модуля
обработки облака точек (point_cloud.cpp)».
```

---

## Советы по работе с Claude

1. **Один раздел за раз.** Никогда не проси написать всё сразу.

2. **Всегда прикрепляй правила оформления** перед генерацией каждого раздела.

3. **Итерации.** После первого варианта проси доработать:
   - «Добавь формулы к разделу X»
   - «Сделай раздел Y длиннее, добавь примеры»
   - «Вставь сюда описание рисунка N»

4. **Цифры — твои.** Claude не знает твоих реальных результатов экспериментов.
   Вставляй данные из `data/results/*.log` и `experiments/results/` сам.

5. **Не переписывай код в отчёт целиком** — только ключевые фрагменты с пояснениями.

6. **Рисунки** — Claude опишет, что должно быть. Схемы архитектуры рисуй в draw.io
   или экспортируй из кода через matplotlib.
