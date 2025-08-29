from functools import cache
from time import time


def fib_nocache(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib_nocache(n - 1) + fib_nocache(n - 2)


@cache
def fib_cache(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib_cache(n - 1) + fib_cache(n - 2)


start_time = time()
print(fib_nocache(35))
print(f"Time taken for fib_nocache: {time() - start_time} seconds")

start_time = time()
print(fib_cache(35))
print(fib_cache.cache_info())
print(f"Time taken for fib_cache: {time() - start_time} seconds")
