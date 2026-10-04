#!/usr/bin/env python3
"""Вспомогательные функции"""

import json
from typing import Any


def load_metadata(file_path: str) -> dict[str, Any]:
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(file_path: str, data: dict[str, Any]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)