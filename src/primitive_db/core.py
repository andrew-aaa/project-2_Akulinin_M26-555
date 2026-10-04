#!/usr/bin/env python3
"""Основаная логика с таблицами"""

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
    print(f'Таблица "{table_name}" успешно удалена')
    return metadata

def list_tables(metadata: dict) -> None:
    if not metadata:
        print("Таблиц нет")
        return

    for name in metadata:
        print(f"- {name}")