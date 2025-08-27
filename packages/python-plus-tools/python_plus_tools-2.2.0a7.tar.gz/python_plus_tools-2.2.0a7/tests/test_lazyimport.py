import os
import importlib
from psutil import Process


def get_memory_usage():
    process = Process(os.getpid())
    return process.memory_info().rss


class LazyImport:
    def __init__(self, module_name):
        self.module_name = module_name
        self._module = None

    def __getattr__(self, name):
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return getattr(self._module, name)


if __name__ == "__main__":
    lazy_import = LazyImport("numpy")
    while True:
        a = input()
        if a == "pi":
            print(lazy_import.pi)
        else:
            print(a)
        print(f"Memory usage: {get_memory_usage() / (1024 * 1024)}MB.")
