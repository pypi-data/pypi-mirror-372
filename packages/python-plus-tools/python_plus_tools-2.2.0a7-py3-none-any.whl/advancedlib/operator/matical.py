from operator import (
    add,
    sub,
    mul,
    truediv,
    floordiv,
    mod,
    pow,
    neg,
    pos,
    abs,
    invert,
    lshift,
    rshift,
    and_,
    or_,
    xor,
    iadd,
    isub,
    imul,
    itruediv,
    ifloordiv,
    imod,
    ipow,
    ilshift,
    irshift,
    iand,
    ior,
    ixor,
)


def select(a: object, b: object, select: bool) -> object:
    """
    Select a value.

    :example:
    >>> import pyplus
    >>> pyplus.tools.dec.select(1, 2, False)
    >>> 1
    >>> pyplus.tools.dec.select(1, 2, True)
    >>> 2

    :param bool select: If select == True,return b, else return a.
    :param object a: If select == False,return a.
    :param object b: If select == True,return b.

    :return object: If select == True,return b, else return a.
    """
    return b if select else a


def space(a, b) -> int:
    """
    :example:
    >>> import pyplus
    >>> pyplus.tools.dec.space(1, 2)
    >>> -1
    >>> pyplus.tools.dec.select(2, 2)
    >>> 0
    >>> pyplus.tools.dec.select(3, 2)
    >>> 1

    :return int:
    If a < b,return -1.If a > b,return 1.If a == b,return 0.
    """
    return (a > b) - (a < b)


cmp = space
