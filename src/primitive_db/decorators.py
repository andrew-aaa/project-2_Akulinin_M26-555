#!/usr/bin/env python3
"""Декораторы и замыкания"""

import functools
import time
from collections.abc import Callable
from typing import Any


def handle_db_errors(func: Callable) -> Callable:
    """Декоратор для централизованной обработки ошибок БД"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована"
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"Произошла ошибка: {e}")
        return None

    return wrapper


def confirm_action(action_name: str) -> Callable:
    """Декоратор-фабрика для запроса подтверждения опасных действий"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            answer = (
                input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
                .strip()
                .lower()
            )
            if answer == "y":
                return func(*args, **kwargs)
            print(f'Операция "{action_name}" отменена')
            return None

        return wrapper

    return decorator


def log_time(func: Callable) -> Callable:
    """Декоратор для замера времени выполнения функций"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")
        return result

    return wrapper


def create_cacher() -> Callable:
    """Функция с замыканием для кэширования результатов запросов"""

    cache: dict[Any, Any] = {}

    def cache_result(key: Any, value_func: Callable[[], Any]) -> Any:
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    def clear() -> None:
        cache.clear()

    cache_result.clear = clear
    return cache_result
