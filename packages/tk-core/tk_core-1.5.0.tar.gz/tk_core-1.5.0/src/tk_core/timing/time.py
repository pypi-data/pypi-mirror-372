from time import perf_counter_ns
from typing import Any, Callable


def timer(ns: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            start_time = perf_counter_ns()
            result = func(*args, **kwargs)
            end_time = perf_counter_ns()
            if ns:
                print(f"Execution time for '{func.__name__}': {end_time - start_time:>10} ns")
            else:
                print(f"Execution time for '{func.__name__}': {(end_time - start_time)/10**9:>10} s")
            return result

        return wrapper

    return decorator


def average_timer(runs: int = 10, ns: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            times = []
            for _ in range(runs):
                start = perf_counter_ns()
                func(*args, **kwargs)
                end = perf_counter_ns()
                times.append(end - start)
            if ns:
                print(f"Average execution time for '{func.__name__}': {sum(times)/len(times):>10} ns")
            else:
                print(f"Average execution time for '{func.__name__}': {sum(times)/len(times)/10**9:>10} s")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class TimerMetaClass(type):
    def __new__(cls, name: str, bases: Any, dct: dict) -> Any:
        for key, value in dct.items():
            if callable(value):
                dct[key] = cls.__timer__(value, name)
        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def __timer__(func: Callable, class_name: str) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            start_time = perf_counter_ns()
            result = func(*args, **kwargs)
            end_time = perf_counter_ns()
            print(f"Execution time for '{class_name}.{func.__name__}': {end_time - start_time}ns")
            return result

        return wrapper


class TimerBaseClass(metaclass=TimerMetaClass):
    pass
