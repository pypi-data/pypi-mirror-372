import psutil


def get_memory() -> float:
    process = psutil.Process()
    return process.memory_info().rss / (1024**2)


def print_memory_usage(name: str) -> None:
    print(f"Memory usage for {name}: {get_memory()}")
