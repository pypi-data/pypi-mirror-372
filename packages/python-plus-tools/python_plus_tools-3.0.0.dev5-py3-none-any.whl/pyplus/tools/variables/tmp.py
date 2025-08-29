import operator as operators

temp_local = {}


def append(**kwargs):
    """Add the variable to temp, if variable in temp, set the variable."""
    for k, v in kwargs.items():
        temp_local[k] = v


def get(key: str = None) -> dict:
    """Get the keys variable, if keys is none, return the temp list, else return the key variable`s value."""
    try:
        return temp_local[key]
    except:
        raise NameError(key + " is not in temp.")


def delete(key: str):
    """Delete the temp keys."""
    try:
        del temp_local[key]
    except:
        raise NameError(key + " is not in temp.")


def set(**kwargs):
    """Same as add."""
    for k, v in kwargs.items():
        temp_local[k] = v


def change(key: str, op, dv):
    try:
        temp_local[key] = op(temp_local[key], dv)
    except:
        raise NameError(key + " is not in temp.")


def in_temp(key: str, false_output=None, true_output=None):
    """Choose the temp, if false_output is not None and key not in temp, print it and return False, else return True.\n
    if true_output is not None and key in temp, print it and return True, else return False.
    """
    if false_output is not None and key not in temp_local:
        print(false_output)
    if true_output is not None and key in temp_local:
        print(true_output)
    return key in temp_local


def clear():
    """Clear the temp."""
    global share_temp
    share_temp = {}


class TempVariable:
    def __init__(self, variable):
        self.variable = variable

    def change(self, do, value):
        return do(self.variable, value)

    def operator(self, do, value):
        return do(self.variable, value)

    def __repr__(self):
        return self.variable

    def __eq__(self, value):
        return self.operator(operators.comparison.eq, value)

    def __lt__(self, value):
        return self.operator(operators.comparison.lt, value)

    def __gt__(self, value):
        return self.operator(operators.comparison.gt, value)

    def __le__(self, value):
        return self.operator(operators.comparison.le, value)

    def __ge__(self, value):
        return self.operator(operators.comparison.ge, value)

    def __add__(self, value):
        return self.change(operators.matical.add, value)

    def __sub__(self, value):
        return self.change(operators.matical.sub, value)

    def __mul__(self, value):
        return self.change(operators.matical.mul, value)

    def __truediv__(self, value):
        return self.change(operators.matical.truediv, value)

    def __floordiv__(self, value):
        return self.change(operators.matical.truediv, value)

    def __or__(self, value):
        return self.change(operators.matical.or_, value)

    def __and__(self, value):
        return self.change(operators.matical.and_, value)

    def __xor__(self, value):
        return self.change(operators.matical.xor, value)

    def __lshift__(self, value):
        return self.change(operators.matical.lshift, value)

    def __rshift__(self, value):
        return self.change(operators.matical.rshift, value)

    def __radd__(self, value):
        return self.change(operators.matical.add, value)

    def __rsub__(self, value):
        return self.change(operators.matical.sub, value)

    def __rmul__(self, value):
        return self.change(operators.matical.mul, value)

    def __rtruediv__(self, value):
        return self.change(operators.matical.truediv, value)

    def __rfloordiv__(self, value):
        return self.change(operators.matical.truediv, value)

    def __ror__(self, value):
        return self.change(operators.matical.or_, value)

    def __rand__(self, value):
        return self.change(operators.matical.and_, value)

    def __rxor__(self, value):
        return self.change(operators.matical.xor, value)

    def __rlshift__(self, value):
        return self.change(operators.matical.lshift, value)

    def __rrshift__(self, value):
        return self.change(operators.matical.rshift, value)

    def __add__(self, value):
        return self.change(operators.matical.add, value)

    def __sub__(self, value):
        return self.change(operators.matical.sub, value)

    def __mul__(self, value):
        return self.change(operators.matical.mul, value)

    def __truediv__(self, value):
        return self.change(operators.matical.truediv, value)

    def __floordiv__(self, value):
        return self.change(operators.matical.truediv, value)

    def __or__(self, value):
        return self.change(operators.matical.or_, value)

    def __and__(self, value):
        return self.change(operators.matical.and_, value)

    def __xor__(self, value):
        return self.change(operators.matical.xor, value)

    def __lshift__(self, value):
        return self.change(operators.matical.lshift, value)

    def __invert__(self, value):
        return self.change(operators.matical.invert, value)
