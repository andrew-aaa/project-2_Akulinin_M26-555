#!/usr/bin/env python3
"""project"""

import shlex
from prompt_toolkit import prompt
from primitive_db.core import (
    DBError,
    InvalidValueError,
    create_table,
    drop_table,
    list_tables
)
from primitive_db.utils import load_metadata, save_metadata


DB_FILE = "db_meta.json"


def print_help() -> None:
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    while True:
        metadata = load_metadata(DB_FILE)

        try:
            user_input = prompt(">>>ВВедите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова")
            continue
        if not args:
            continue

        command, rest = args[0], args[1:]
        try:
            if command == "create_table":
                if len(rest) < 2:
                    raise InvalidValueError(" ".join(rest) or command)
                create_table(metadata, rest[0], rest[1:])
                save_metadata(DB_FILE, metadata)

            elif command == "drop_table":
                if len(rest) != 1:
                    raise InvalidValueError(" ".join(rest) or command)
                drop_table(metadata, rest[0])
                save_metadata(DB_FILE, metadata)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "help":
                if rest:
                    raise InvalidValueError(" ".join(rest))
                print_help()

            elif command == "exit":
                if rest:
                    raise InvalidValueError(" ".join(rest))
                return

            else:
                print(f"Функции {command} нет. Попробуйте снова")

        except DBError as e:
            print(f"Ошибка: {e}")
        except InvalidValueError as e:
            print(f"Некорректное значение: {e.value}. Попробуйте снова")

