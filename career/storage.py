from __future__ import annotations

import json
from pathlib import Path


DATA_DIR = Path(".data")
SETTINGS_FILE = DATA_DIR / "settings.json"


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}
