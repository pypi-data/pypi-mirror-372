from typing_extensions import Callable, Tuple, Any
from os import *
import psutil
import subprocess
from pathlib import Path


def get_memory_usage(
    args: Tuple[Any] = (),
    kwargs: dict[str, Any] = {},
    memory_usage_output_limit: int = 10,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            import tracemalloc

            tracemalloc.start()

            before_snapshot = tracemalloc.take_snapshot()

            func(*args, **kwargs)

            after_snapshot = tracemalloc.take_snapshot()

            total_increase = sum(
                stat.size_diff
                for stat in after_snapshot.compare_to(before_snapshot, "traceback")
            )
            print(f"\nMemory usage: {total_increase/1024**2:.2f} MB\n")

            top_stats = after_snapshot.compare_to(before_snapshot, "lineno")

            print("Memory usage by file:")
            for stat in top_stats[
                : (
                    memory_usage_output_limit
                    if memory_usage_output_limit is not None
                    else -1
                )
            ]:
                print(f"▲ {stat.size_diff/1024:.1f} KB | {stat.traceback.format()[-1]}")
            tracemalloc.stop()
            return func(*args, **kwargs)

        return wrapper

    return decorator


del Callable, Tuple, Any
