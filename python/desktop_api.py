"""DesktopAPI — JS-API объект для pywebview.

Методы вызываются из JS через window.pywebview.api.<method>().
"""
from __future__ import annotations

import webview


class DesktopAPI:
    def get_folder(self) -> str:
        """Нативный диалог выбора папки. Возвращает путь или пустую строку."""
        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else ""
