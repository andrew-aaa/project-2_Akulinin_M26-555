#!/usr/bin/env python3
"""project"""

import shlex
from prompt_toolkit import prompt
from prettytable import PrettyTable
from primitive_db.core import (
    DBError,
    InvalidValueError,
    create_table,
    drop_table,
    list_tables,
    insert,
    select,
    update,
    delete,
    table_info
)
from primitive_db.parser import (
    parse_insert,
    parse_select,
    parse_update,
    parse_delete
)
from primitive_db.utils import load_metadata, save_metadata, load_table_data, save_table_data


DB_FILE = "db_meta.json"


def print_help() -> None:
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
    print_help()
    while True:
        metadata = load_metadata(DB_FILE)

        try:
            user_input = prompt(">>>ВВедите команду: ").strip()
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
                    raise InvalidValueError(user_input)
                create_table(metadata, args[1], args[2:])
                save_metadata(DB_FILE, metadata)

            elif command == "drop_table":
                args = shlex.split(user_input)
                if len(args) != 2:
                    raise InvalidValueError(user_input)
                drop_table(metadata, args[1])
                save_metadata(DB_FILE, metadata)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "help":
                print_help()

            elif command == "exit":
                return

            elif command == "insert":
                table_name, values = parse_insert(user_input)
                if table_name not in metadata:
                    raise DBError(f'Таблица "{table_name}" не существует')
                table_data = load_table_data(table_name)
                table_data, new_id = insert(metadata, table_name, table_data, values)
                save_table_data(table_name, table_data)
                print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}"')

            elif command == "select":
                table_name, col, val = parse_select(user_input)
                if table_name not in metadata:
                    raise DBError(f'Таблица "{table_name}" не существует')
                table_data = load_table_data(table_name)
                if not isinstance(table_data, list):
                    table_data = []
                record = select(table_data, metadata, table_name, col, val)
                pt = PrettyTable()
                cols = [c["name"] for c in metadata[table_name]]
                pt.field_names = cols
                for row in record:
                    pt.add_row([row.get(c, "None") for c in cols])
                print(pt)

            elif command == "update":
                table_name, set_col, set_val, where_col, where_val = parse_update(user_input)
                if table_name not in metadata: 
                    raise DBError(f'Таблица "{table_name}" не существует')
                table_data = load_table_data(table_name)
                table_data, updated_ids = update(table_data, metadata, table_name, set_col, set_val, where_col, where_val)
                save_table_data(table_name, table_data)
                if updated_ids:
                    for uid in updated_ids:
                        print(f'Запись с ID={uid} в таблице "{table_name}" успешно обновлена')
                else:
                    print("Подходящих записей для обновления не найдено")

            elif command == "delete":
                table_name, where_col, where_val = parse_delete(user_input)
                if table_name not in metadata:
                    raise DBError(f'Таблица "{table_name}" не существует')
                table_data = load_table_data(table_name)
                table_data, deleted_ids = delete(table_data, metadata, table_name, where_col, where_val)
                save_table_data(table_name, table_data)
                if deleted_ids:
                    for uid in deleted_ids:
                        print(f'Запись с ID={uid} успешно удалена из таблицы "{table_name}"')
                else:
                    print("Подходящих записей для удаления не найдено")

            elif command == "info":
                args = shlex.split(user_input)
                if len(args) != 2: 
                    raise InvalidValueError(user_input)
                table_name = args[1]
                if table_name not in metadata:
                    raise DBError(f'Таблица "{table_name}" не существует')
                table_data = load_table_data(table_name)
                table_info(metadata, table_name, table_data)

            else:
                print(f"Функции {command} нет. Попробуйте снова")

        except DBError as e:
            print(f"Ошибка: {e}")
        except ValueError as e:
            print(f"Ошибка: {e}")
        except InvalidValueError as e:
            print(f"Некорректное значение: {e.value}. Попробуйте снова")

