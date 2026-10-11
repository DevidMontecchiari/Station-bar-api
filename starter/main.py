"""Run: python -m uvicorn main:app --reload"""
import os
from pathlib import Path
from bar_api.api import create_app

app = create_app(Path(os.environ.get("BAR_DATA_FILE", Path(__file__).with_name("data.json"))))
