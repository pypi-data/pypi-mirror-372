"""
This is a moudle for python unit calculation
Use this moudle,plese write:
`Unit()` or other class in this moudle.
If you want to create new unit class,please use:
"""

import operator
from advancedlib import operator as operators

from pathlib import Path
from os import getenv
from advancedlib.importlib import LazyImport

from . import units

from toml import load

try:
    o1 = open(Path(getenv("appdata"), "xystudio", "pyplus", "config.toml"))
    o2 = open(Path(".xystudio", "pyplus", "config.toml").absolute())

    config = load(o1) | load(o2)

    o1.close()
    o2.close()
except FileNotFoundError:
    config = {}

if config.get("import", {}).get("lazy", True):
    pyscience = LazyImport("pyplus.science.pyscience")
else:
    from . import pyscience

del load, getenv, Path, LazyImport

__all__ = ["units", "pyscience", "science", "operators", "operator"]
