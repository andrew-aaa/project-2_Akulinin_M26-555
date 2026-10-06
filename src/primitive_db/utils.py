#!/usr/bin/env python3
"""Вспомогательные функции"""

import json
import os
from typing import Any

from .constants import DATA_DIR, META_FILE


def load_metadata(file_path: str = META_FILE) -> dict[str, Any]:
    """Загружает метаданные базы данных из JSON-файла"""

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_metadata(file_path: str, data: dict[str, Any]) -> None:
    """Сохраняет метаданные базы данных в JSON-файл"""

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_table_data(table_name: str) -> list[dict]:
    """Загружает данные конкретной таблицы из соответствующего JSON-файла"""

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
    """Сохраняет данные таблицы в JSON-файл в директории data/"""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    path = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
