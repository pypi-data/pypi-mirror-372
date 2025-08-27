from pyplus.science.units import Version
from pdb import *


class DebugError(BaseException):
    def __init__(self, *args):
        super().__init__(*args)


NO_DEFIND = None
NOT_IN_DEBUG = False
IN_DEBUG = True
THIS_FILE = "__main__"

debug = NO_DEFIND
START = "start"
END = "end"

ticks = {}


def stop():
    "stop and press any key to continue."
    input("press any key to continue.")


def run(code, judge: bool = True):
    """if judge is True, run code.
    >>> run('print("hello world!")')
    'hello world!'
    >>> run('print("hello world!")', False)
    """
    if judge:
        exec(code)


def output(string, judge: bool = True):
    """if judge is True, print string.

    >>> output("hello world!")
    'hello world!'
    >>> output("hello world!", False)
    """
    if judge:
        run("print('" + string + "')")


def judge(main_code, judge: bool, else_code: str = ""):
    """fast Ternary Operator
    >>> judge("print(1)", 1!=1, "a=2;print(a)")
    2
    """
    if judge:
        exec(main_code)
    else:
        exec(else_code)


def judge_false_raise_error():
    assert not (debug is bool or debug is None or debug in [1, 2])


def in_debug() -> bool:
    "is debug."
    judge_false_raise_error()
    return debug


def typejudge(judge_object: list, judge_type: list[type]) -> bool:
    assert (
        len(judge_object) == len(judge_type)
        and isinstance(judge_type, list)
        and isinstance(judge_object, list)
    )
    typeOp = []
    for i in range(len(judge_object)):
        typeOp.append(isinstance(judge_object[i], judge_type[i]))
    return all(typeOp)


def tick(
    type: str,
    name: str,
    output: bool = True,
    unit: int = 1000,
    end: str = "s",
    round_: bool = False,
    out_name: bool = False,
    **kwargs,
) -> str:
    from time import time

    assert typejudge(
        [type, name, output, unit, end, round_, out_name],
        [str, str, bool, int, str, bool, bool],
    )
    if type == START:
        if name in ticks:
            raise NameError("name'" + name + "'is in clock list.")
        else:
            ticks[name] = time()
    elif type == END:
        this_tick = ticks[name]
        del ticks[name]
        out = (
            round((time() - this_tick) * 1000 / unit)
            if round_
            else (time() - this_tick) * 1000 / unit
        )
        if output:
            print(name, out, end=end + "\n")
        if out_name:
            return name, out
        return out
    else:
        raise KeyError("key'" + str(type) + "'is not a tick type.")


def do(code):
    """run the Pdb code."""
    Pdb.run(code)


def func_debug():
    def decorator(func):
        import time

        def wrapper(*a, **kw):
            t1 = time.time()
            res = func(*a, **kw)
            t2 = time.time()
            print(f"function {func.__name__}\nreturn {res}\nuse {(t2-t1)*1000}ms.")
            return res

        return wrapper

    return decorator
