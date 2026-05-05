"""FastAPI приложение: REST + WebSocket."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Scanner API", version="0.1.0")

# TODO: подключить роутеры (upload, status, download)
# TODO: app.mount("/", StaticFiles(directory=..., html=True), name="web")
