#!/usr/bin/env python3
"""Вспомогательные функции"""

import json
import os
from typing import Any


DATA_DIR = "data"
DB_FILE = "db_meta.json"

def load_metadata(file_path: str = DB_FILE) -> dict[str, Any]:
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(file_path: str, data: dict[str, Any]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_table_data(table_name: str) -> list[dict]:
    path = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_table_data(table_name: str, data: list[dict]) -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    path = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
