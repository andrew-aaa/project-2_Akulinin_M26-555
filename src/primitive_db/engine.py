#!/usr/bin/env python3
"""Главный интерактивный цикл обработки пользовательского ввода"""

import shlex

from prettytable import PrettyTable
from prompt_toolkit import prompt

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    table_info,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_delete, parse_insert, parse_select, parse_update
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

from .constants import META_FILE

db_cacher = create_cacher()


def print_help() -> None:
    """Выводит справочную информацию по доступным командам"""

    print("\n***Операции с данными***")
    print("\nФункции:")
    print(" insert into  values (, , ...) - создать запись.")
    print(" select from  where  =  - прочитать записи по условию.")
    print(" select from  - прочитать все записи.")
    print(" update  set  =  where  =  - обновить запись.")
    print(" delete from  where  =  - удалить запись.")
    print(" info  - вывести информацию о таблице.")
    print(" create_table   .. - создать таблицу")
    print(" list_tables - показать список всех таблиц")
    print(" drop_table  - удалить таблицу")

    print("\n-  exit - выход из программы")
    print("-  help - справочная информация\n")


def run() -> None:
    """Запускает цикл взаимодействия с БД"""

    print_help()

    while True:
        metadata = load_metadata(META_FILE)

        try:
            user_input = prompt(">>> Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not user_input:
            continue

        command = user_input.split()[0].lower()

        try:
            if command == "create_table":
                args = shlex.split(user_input)
                if len(args) < 3:
                    print(f"Некорректная команда: {user_input}")
                    continue
                res = create_table(metadata, args[1], args[2:])
                if res is not None:
                    save_metadata(META_FILE, metadata)

            elif command == "drop_table":
                args = shlex.split(user_input)
                if len(args) != 2:
                    print(f"Некорректная команда: {user_input}")
                    continue
                res = drop_table(metadata, args[1])
                if res is not None:
                    save_metadata(META_FILE, metadata)
                    db_cacher.clear()

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "help":
                print_help()

            elif command == "exit":
                return

            elif command == "insert":
                table_name, values = parse_insert(user_input)
                table_data = load_table_data(table_name)
                res = insert(metadata, table_name, table_data, values)
                if res is not None:
                    table_data, new_id = res
                    save_table_data(table_name, table_data)
                    db_cacher.clear()
                    print(
                        f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}"'
                    )

            elif command == "select":
                table_name, col, val = parse_select(user_input)
                table_data = load_table_data(table_name)
                cache_key = (table_name, col, val, str(table_data))
                records = db_cacher(
                    cache_key,
                    lambda td=table_data, md=metadata, tn=table_name, c=col, v=val: select(
                        td, md, tn, c, v
                    ),
                )
                if records is not None:
                    pt = PrettyTable()
                    cols = [c["name"] for c in metadata[table_name]]
                    pt.field_names = cols
                    for row in records:
                        if isinstance(row, dict):
                            pt.add_row([row.get(c, "None") for c in cols])
                    print(pt)

            elif command == "update":
                table_name, set_col, set_val, where_col, where_val = parse_update(
                    user_input
                )
                table_data = load_table_data(table_name)
                res = update(
                    table_data,
                    metadata,
                    table_name,
                    set_col,
                    set_val,
                    where_col,
                    where_val,
                )
                if res is not None:
                    table_data, updated_ids = res
                    save_table_data(table_name, table_data)
                    db_cacher.clear()
                    if updated_ids:
                        for uid in updated_ids:
                            print(
                                f'Запись с ID={uid} в таблице "{table_name}" успешно обновлена'
                            )
                    else:
                        print("Подходящих записей для обновления не найдено")

            elif command == "delete":
                table_name, where_col, where_val = parse_delete(user_input)
                table_data = load_table_data(table_name)
                res = delete(table_data, metadata, table_name, where_col, where_val)
                if res is not None:
                    table_data, deleted_ids = res
                    save_table_data(table_name, table_data)
                    db_cacher.clear()
                    if deleted_ids:
                        for uid in deleted_ids:
                            print(
                                f'Запись с ID={uid} успешно удалена из таблицы "{table_name}"'
                            )
                    else:
                        print("Подходящих записей для удаления не найдено.")

            elif command == "info":
                args = shlex.split(user_input)
                if len(args) != 2:
                    print(f"Некорректная команда: {user_input}")
                    continue
                table_name = args[1]
                table_data = load_table_data(table_name)
                table_info(metadata, table_name, table_data)

            else:
                print(f"Функции {command} нет. Попробуйте снова")

        except ValueError as e:
            print(f"Ошибка парсинга команды: {e}")
