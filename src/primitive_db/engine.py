#!/usr/bin/env python3
"""project"""

from prompt_toolkit import prompt

MENU = (
    "<command> exit - выйти из программы\n"
    "<command> help - справочная информация"
)


def _print_menu() -> None:
    """Напечатать список доступных команд."""
    print(MENU)


def welcome() -> None:
    """Поприветствовать пользователя и запустить основной цикл команд."""
    print("Первая попытка запустить проект!")
    print()

    print("***")
    _print_menu()

    while True:
        command = prompt("Введите команду: ").strip()

        if command == "exit":
            print("До свидания!")
            return
        elif command == "help":
            print()
            _print_menu()
        else:
            print(f"Неизвестная команда: {command}")