"""desktop.py — нативное окно pywebview поверх локального FastAPI.

Запуск:
    python python/desktop.py
    # или через PowerShell:
    .\\scripts\\run_desktop.ps1
"""
from __future__ import annotations

import sys
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

# python/ должен быть в sys.path для импорта api.server
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn
import webview

from api.server import app
from desktop_api import DesktopAPI

_HOST = "127.0.0.1"
_PORT = 8765
_URL  = f"http://{_HOST}:{_PORT}/"


def _start_server() -> None:
    uvicorn.run(app, host=_HOST, port=_PORT, log_level="error")


def _wait_for_server(timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(_URL + "api/status", timeout=1)
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def main() -> None:
    t = threading.Thread(target=_start_server, daemon=True)
    t.start()

    if not _wait_for_server():
        print("Сервер не запустился за 10 секунд", file=sys.stderr)
        sys.exit(1)

    window = webview.create_window(
        title="3D Scanner",
        url=_URL,
        js_api=DesktopAPI(),
        width=1280,
        height=800,
        min_size=(800, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
