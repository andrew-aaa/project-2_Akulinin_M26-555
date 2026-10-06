#!/usr/bin/env python3
"""Основная бизнес-логика работы с таблицами и записями"""

import os
from typing import Any

from .constants import DATA_DIR, VALID_TYPES
from .decorators import confirm_action, handle_db_errors, log_time
from .parser import cast_type


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создает новую таблицу и обновляет метаданные"""

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует')

    parsed = []
    for col in columns:
        if ":" not in col:
            raise ValueError(f"Некорректный формат столбца: {col}")

        name, dtype = col.split(":")
        if dtype not in VALID_TYPES:
            raise ValueError(f"Неподдерживаемый тип '{dtype}' для столбца '{name}'")

        parsed.append({"name": name, "type": dtype})

    if all(c["name"] != "ID" for c in parsed):
        parsed.insert(0, {"name": "ID", "type": "int"})

    metadata[table_name] = parsed

    display = ", ".join(f"{c['name']}:{c['type']}" for c in parsed)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {display}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных и связанный файл данных"""

    if table_name not in metadata:
        raise KeyError(table_name)

    del metadata[table_name]

    path = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(path):
        os.remove(path)

    print(f'Таблица "{table_name}" успешно удалена')
    return metadata


def list_tables(metadata: dict) -> None:
    """Выводит список существующих таблиц"""

    if not metadata:
        print("Таблиц нет")
        return

    for name in metadata:
        print(f"- {name}")


@handle_db_errors
@log_time
def insert(
    metadata: dict, table_name: str, table_data: list[dict], values: list[str]
) -> tuple[list[dict], int]:
    """Добавляет новую запись в таблицу с генерацией автоинкрементного ID"""

    if table_name not in metadata:
        raise KeyError(table_name)

    columns = metadata[table_name]
    if len(values) != len(columns) - 1:
        raise ValueError(
            f"Ожидается {len(columns) - 1} значений, получено {len(values)}"
        )

    new_record: dict[str, Any] = {}
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    new_record["ID"] = new_id

    for col, val_str in zip(columns[1:], values):
        new_record[col["name"]] = cast_type(val_str, col["type"])

    table_data.append(new_record)
    return table_data, new_id


@handle_db_errors
@log_time
def select(
    table_data: list[dict],
    metadata: dict,
    table_name: str,
    where_col: str | None = None,
    where_val_str: str | None = None,
) -> list[dict]:
    """Выбирает записи из таблицы по опциональному условию"""

    if table_name not in metadata:
        raise KeyError(table_name)

    if not where_col:
        return table_data

    col_type = next(
        (c["type"] for c in metadata[table_name] if c["name"] == where_col),
        None,
    )
    if not col_type:
        raise KeyError(where_col)

    where_val = cast_type(where_val_str, col_type)
    return [row for row in table_data if row.get(where_col) == where_val]


@handle_db_errors
def update(
    table_data: list[dict],
    metadata: dict,
    table_name: str,
    set_col: str,
    set_val_str: str,
    where_col: str,
    where_val_str: str,
) -> tuple[list[dict], list[int]]:
    """Обновляет записи в таблице по заданному условию"""

    if table_name not in metadata:
        raise KeyError(table_name)

    set_type = next(
        (c["type"] for c in metadata[table_name] if c["name"] == set_col), None
    )
    where_type = next(
        (c["type"] for c in metadata[table_name] if c["name"] == where_col),
        None,
    )

    if not set_type:
        raise KeyError(set_col)
    if not where_type:
        raise KeyError(where_col)

    set_val = cast_type(set_val_str, set_type)
    where_val = cast_type(where_val_str, where_type)

    updated_ids = []
    for row in table_data:
        if row.get(where_col) == where_val:
            row[set_col] = set_val
            updated_ids.append(row["ID"])

    return table_data, updated_ids


@handle_db_errors
@confirm_action("удаление записи")
def delete(
    table_data: list[dict],
    metadata: dict,
    table_name: str,
    where_col: str,
    where_val_str: str,
) -> tuple[list[dict], list[int]]:
    """Удаляет записи из таблицы по условию"""

    if table_name not in metadata:
        raise KeyError(table_name)

    where_type = next(
        (c["type"] for c in metadata[table_name] if c["name"] == where_col),
        None,
    )
    if not where_type:
        raise KeyError(where_col)

    where_val = cast_type(where_val_str, where_type)

    deleted_ids = []
    new_data = []
    for row in table_data:
        if row.get(where_col) == where_val:
            deleted_ids.append(row["ID"])
        else:
            new_data.append(row)

    return new_data, deleted_ids


@handle_db_errors
def table_info(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    """Выводит сводную информацию о структуре и количестве записей в таблице"""

    if table_name not in metadata:
        raise KeyError(table_name)

    cols = ", ".join(f"{c['name']}:{c['type']}" for c in metadata[table_name])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(table_data)}")
