#!/usr/bin/env python3
"""Основаная логика с таблицами"""

import os
from .parser import cast_type
from .utils import DATA_DIR

VALID_TYPES = {"int", "str", "bool"}


class DBError(Exception):
    pass


class InvalidValueError(Exception):
    def __init__(self, value: str):
        self.value = value


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        raise DBError(f'Таблица "{table_name}" уже существует')

    parsed = []
    for col in columns:
        if ":" not in col:
            raise InvalidValueError(col)

        name, dtype = col.split(":")
        if dtype not in VALID_TYPES:
            raise InvalidValueError(col)

        parsed.append({"name": name, "type": dtype})

    if all(c["name"] != "ID" for c in parsed):
        parsed.insert(0, {"name": "ID", "type": "int"})

    metadata[table_name] = parsed

    display = ", ".join(f'{c["name"]}:{c["type"]}' for c in parsed)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {display}')
    return metadata

def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        raise DBError(f'Таблица "{table_name}" не существует')

    del metadata[table_name]

    path = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(path):
        os.remove(path)
    
    print(f'Таблица "{table_name}" успешно удалена')
    return metadata

def list_tables(metadata: dict) -> None:
    if not metadata:
        print("Таблиц нет")
        return

    for name in metadata:
        print(f"- {name}")

def insert(metadata: dict, table_name: str, table_data: list[dict], values: list[str]) -> tuple[list[dict], int]:
    columns = metadata[table_name]
    if len(values) != len(columns) - 1:
        raise DBError(f'Ожидается {len(columns) - 1} значений, получено {len(values)}')

    new_record = {}
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    new_record["ID"] = new_id

    for col, val_str in zip(columns[1:], values):
        try:
            new_record[col["name"]] = cast_type(val_str, col["type"])
        except ValueError as e:
            raise InvalidValueError(str(e))

    table_data.append(new_record)
    return table_data, new_id

def select(table_data: list[dict], metadata: dict, table_name: str, where_col: str = None, where_val_str: str = None) -> list[dict]:
    if not where_col:
        return table_data

    col_type = next((c["type"] for c in metadata[table_name] if c["name"] == where_col), None)
    if not col_type:
        raise DBError(f'Столбец "{where_col}" не найден')

    try:
        where_val = cast_type(where_val_str, col_type)
    except ValueError as e:
        raise InvalidValueError(str(e))

    return [r for r in table_data if r.get(where_col) == where_val]

def update(table_data: list[dict], metadata: dict, table_name: str, set_col: str, set_val_str: str, where_col: str, where_val_str: str) -> tuple[list[dict], list[int]]:
    set_type = next((c["type"] for c in metadata[table_name] if c["name"] == set_col), None)
    if not set_type:
        raise DBError(f'Столбец "{set_col}" не найден')

    where_type = next((c["type"] for c in metadata[table_name] if c["name"] == where_col), None)
    if not where_type:
        raise DBError(f'Столбец "{where_col}" не найден')

    try:
        set_val = cast_type(set_val_str, set_type)
        where_val = cast_type(where_val_str, where_type)
    except ValueError as e:
        raise InvalidValueError(str(e))

    updated_ids = []
    for row in table_data:
        if row.get(where_col) == where_val:
            row[set_col] = set_val
            updated_ids.append(row["ID"])

    return table_data, updated_ids

def delete(table_data: list[dict], metadata: dict, table_name: str, where_col: str, where_val_str: str) -> tuple[list[dict], list[int]]:
    where_type = next((c["type"] for c in metadata[table_name] if c["name"] == where_col), None)
    if not where_type:
        raise DBError(f'Столбец "{where_col}" не найден')

    try:
        where_val = cast_type(where_val_str, where_type)
    except ValueError as e:
        raise InvalidValueError(str(e))

    deleted_ids, new_data = [], []
    for row in table_data:
        if row.get(where_col) == where_val:
            deleted_ids.append(row["ID"])
        else:
            new_data.append(row)

    return new_data, deleted_ids

def table_info(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    cols = ", ".join(f'{c["name"]}:{c["type"]}' for c in metadata[table_name])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(table_data)}")
