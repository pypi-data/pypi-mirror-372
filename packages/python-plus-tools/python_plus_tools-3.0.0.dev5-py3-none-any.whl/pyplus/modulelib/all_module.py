from pathlib import Path
from sys import prefix

from toml import load, dump
from site import getsitepackages

INITIALIZED = False
folder_path = Path(prefix, "Lib")
all_entries = [entry.name for entry in folder_path.iterdir()]
files = [entry.name for entry in folder_path.iterdir() if entry.is_file()]
dirs = [entry.name for entry in folder_path.iterdir() if entry.is_dir()]

filter_list = ["site-packages", "this.py", "antigravity.py", "__pycache__"]

filtered_list = [item for item in files + dirs if item not in filter_list]

texts = ["INITIALIZED = True"]

for i in filtered_list:
    try:
        __import__(i.split(".py")[0])
        texts.append(f"import {i.split('.py')[0]}")
    except (ImportError, ModuleNotFoundError, DeprecationWarning):
        pass

with open(
    getsitepackages()[1] + "/pyplus/data/config/all_module.py", "w", encoding="utf-8"
) as f:
    f.write("\n".join(texts))

del load, dump, getsitepackages
