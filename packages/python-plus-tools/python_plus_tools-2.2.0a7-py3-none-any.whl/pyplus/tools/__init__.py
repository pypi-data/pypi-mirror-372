import decorators
from img_fit import latex2text as latex

from . import (
    colors,
    dec,
    database_convert,
    formula,
    # password,
    permission,
    stack,
    tag,
    update,
    web,
    variables,
    pycppio,
)
from argparse import Namespace
import backup

# from . import () # deprecated moudle


def wait(operator: bool):
    """
    Please use it in subprocess.
    """
    while not operator:
        pass


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
