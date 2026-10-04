#!/usr/bin/env python3
"""Парсер для обработки команд"""

import re
from typing import Any


def cast_type(val: str, expected_type: str) -> Any:
    val = val.strip()
    if expected_type == "int":
        return int(val)
    elif expected_type == "bool":
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        raise ValueError(f"Ожидается true/false для bool, получено: {val}")
    elif expected_type == "str":
        if not ((val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'"))):
            raise ValueError(f"Строковые значения должны быть в кавычках: {val}")
        return val[1:-1]
    else:
        raise ValueError(f"Неизвестный тип: {expected_type}")

def parse_insert(user_input: str) -> tuple[str, list[str]]:
    match = re.match(r'insert\s+into\s+(\w+)\s+values\s*\((.*)\)', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Неверный формат команды insert")

    table_name = match.group(1)
    raw_values = match.group(2)

    tokens = []
    current = ""
    flag = False
    for char in raw_values:
        if char in ("'", '"'):
            flag = not flag
            current += char
        elif char == ',' and not flag:
            tokens.append(current.strip())
            current = ""
        else:
            current += char

    if current:
        tokens.append(current.strip())

    return table_name, tokens

def parse_select(user_input: str) -> tuple[str, str | None, str | None]:
    match = re.match(r'select\s+from\s+(\w+)(?:\s+where\s+(\w+)\s*=\s*(.+))?', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Неверный формат команды select")

    return match.group(1), match.group(2), match.group(3)

def parse_update(user_input: str) -> tuple[str, str, str, str, str]:
    match = re.match(r'update\s+(\w+)\s+set\s+(\w+)\s*=\s*(.+?)\s+where\s+(\w+)\s*=\s*(.+)', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Неверный формат команды update")

    return match.group(1), match.group(2), match.group(3).strip(), match.group(4), match.group(5).strip()

def parse_delete(user_input: str) -> tuple[str, str, str]:
    match = re.match(r'delete\s+from\s+(\w+)\s+where\s+(\w+)\s*=\s*(.+)', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Неверный формат команды delete")

    return match.group(1), match.group(2), match.group(3).strip()
