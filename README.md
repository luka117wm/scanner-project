# Scanner 3D

Автоматизированная система получения 3D-моделей для аддитивного производства
методом фотограмметрии.

**Вход:** фотографии (JPEG/PNG) или видео → **Выход:** STL для 3D-печати.

---

## Быстрый старт (Windows, PowerShell)

### 1. Зависимости

```powershell
# vcpkg + Eigen3
cd D:\
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg; .\bootstrap-vcpkg.bat
.\vcpkg install eigen3:x64-windows

# Python окружение
cd D:\3ds\scanner-project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e python\
```

### 2. COLMAP

Скачать с https://github.com/colmap/colmap/releases и распаковать в `tools\colmap\`.

### 3. nanoflann

Скачать `nanoflann.hpp` с https://github.com/jlblancoc/nanoflann/releases
и поместить в `cpp\third_party\nanoflann\nanoflann.hpp`.

### 4. Сборка C++

```powershell
mkdir build; cd build
cmake ..\cpp -G "Visual Studio 17 2022" -A x64 `
    -DCMAKE_PREFIX_PATH="D:\vcpkg\installed\x64-windows" `
    -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
cmake --build . --config Release
Copy-Item build\Release\_scanner_cpp.pyd python\scanner\
```

### 5. Использование

```powershell
# Из фотографий
python -m scanner scan --images .\photos --output model.stl

# Из видео
python -m scanner scan --video recording.mp4 --output model.stl

# Веб-интерфейс
python -m scanner serve --port 8000
```

---

## Структура

| Папка | Назначение |
|-------|-----------|
| `cpp/` | C++ ядро (облако точек, меш, ремонт, печать) |
| `python/scanner/` | Python пайплайн и CLI |
| `python/api/` | FastAPI + WebSocket сервер |
| `web/` | Three.js вьюер |
| `experiments/` | Скрипты для дипломных экспериментов |
| `tools/colmap/` | COLMAP бинарники (не в git) |
| `data/` | Тестовые данные (не в git) |

---

## Требования

- Windows 10/11
- Python 3.11+
- Visual Studio Build Tools 2022 (MSVC v143)
- CMake 3.16+
- vcpkg с Eigen3
- COLMAP (предсобранные .exe)
