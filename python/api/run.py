"""Точка входа: python python/api/run.py"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn
from api.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
