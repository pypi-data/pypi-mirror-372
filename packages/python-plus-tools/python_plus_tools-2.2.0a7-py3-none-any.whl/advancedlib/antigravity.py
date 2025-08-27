from toml import load
from os import getenv
from pathlib import Path

try:
    o1 = open(Path(getenv("appdata"), "xystudio", "pyplus", "config.toml"))
    o2 = open(Path(".xystudio", "pyplus", "config.toml").absolute())

    config = load(o1) | load(o2)

    o1.close()
    o2.close()
except FileNotFoundError:
    config = {}

del load, getenv, Path


def open_web():
    import webbrowser

    webbrowser.open("https://xkcd.com/353/")


if config.get("advancedlib", {"showAntigravityWeb": False}).get(
    "showAntigravityWeb", False
):
    open_web()


def geohash(latitude, longitude, datedow):
    import hashlib

    """Compute geohash() using the Munroe algorithm.

    >>> geohash(37.421542, -122.085589, b'2005-05-26-10458.68')
    37.857713 -122.544543

    """
    # https://xkcd.com/426/
    h = hashlib.md5(datedow, usedforsecurity=False).hexdigest()
    p, q = [("%f" % float.fromhex("0." + x)) for x in (h[:16], h[16:32])]
    print("%d%s %d%s" % (latitude, p[1:], longitude, q[1:]))
