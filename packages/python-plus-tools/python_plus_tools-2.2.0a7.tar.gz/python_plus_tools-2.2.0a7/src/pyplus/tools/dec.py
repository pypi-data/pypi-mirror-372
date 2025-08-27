from advancedlib.itertools import IteratorCalculator
from advancedlib.operator.matical import select, space, cmp
from typing_extensions import override, Union, TypeAlias


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


class dint(int):
    def __new__(cls, value: int):
        instance = super().__new__(cls, value)
        instance.use_dec = value
        return instance

    def __iter__(self):
        return iter([dint(i) for i in str(self)])

    def __getattr__(self, index):
        return dint(str(self)[index])

    def __len__(self):
        return len(str(self))

    @override
    def __lshift__(self, value):
        if self.use_dec:
            return dint(self * (10**value))
        else:
            return super().__lshift__(value)

    @override
    def __rshift__(self, value: int):
        if self.use_dec:
            o = str(self)[:-value]
            return select(dint(0), dint(o), o != "")
        else:
            return super().__rshift__(value)

    @override
    def __or__(self, value):
        if self.use_dec:
            o = ""
            str_v = [str(self), str(value)]

            if len(str_v[0]) > len(str_v[1]):
                o += str_v[0][: len(str_v[0]) - len(str_v[1])]
                str_v[0] = str_v[0][len(str_v[0]) - len(str_v[1]) :]
            elif len(str_v[1]) > len(str_v[0]):
                o += str_v[1][: len(str_v[1]) - len(str_v[0])]
                str_v[1] = str_v[1][len(str_v[1]) - len(str_v[0]) :]

            for index in range(len(str_v[0])):
                o += select(
                    str_v[0][index], str_v[1][index], str_v[0][index] != str_v[1][index]
                )
            return dint(o)
        else:
            return super().__or__(value)

    @override
    def __and__(self, value):
        if self.use_dec:
            o = ""
            str_v = [str(self), str(value)]

            if len(str_v[0]) > len(str_v[1]):
                o += str_v[0][: len(str_v[0]) - len(str_v[1])]
                str_v[0] = str_v[0][len(str_v[0]) - len(str_v[1]) :]
            elif len(str_v[1]) > len(str_v[0]):
                o += str_v[1][: len(str_v[1]) - len(str_v[0])]
                str_v[1] = str_v[1][len(str_v[1]) - len(str_v[0]) :]

            for index in range(len(str_v[0])):
                o += select(
                    str_v[0][index],
                    str_v[1][index],
                    space(str_v[0][index], str_v[1][index]) <= 0,
                )
            return dint(o)
        else:
            return super().__and__(value)

    @override
    def __invert__(self):
        if self.use_dec:
            o = ""
            for index in self:
                o += str(select(index + 5, index - 5, index >= 5))
            return dint(o)
        else:
            return super().__invert__()

    @override
    def __xor__(self, value):
        if self.use_doc:
            o = ""
            str_v = [str(self), str(value)]

            if len(str_v[0]) > len(str_v[1]):
                o += str_v[0][: len(str_v[0]) - len(str_v[1])]
                str_v[0] = str_v[0][len(str_v[0]) - len(str_v[1]) :]
            elif len(str_v[1]) > len(str_v[0]):
                o += str_v[1][: len(str_v[1]) - len(str_v[0])]
                str_v[1] = str_v[1][len(str_v[1]) - len(str_v[0]) :]

            for index in range(len(str_v[0])):
                o += select(
                    str_v[1][index],
                    str_v[0][index],
                    space(str_v[0][index], str_v[1][index]) <= 0,
                )

            return dint(o)
        else:
            return super().__xor__(value)


class istr(str):
    def __new__(cls, string: str):
        instance = super().__new__(cls, string)
        instance.str = string
        instance.use_defalt = False
        return instance

    @property
    def all_char_unicode(self) -> list[int]:
        """Get some string unicode."""
        return [ord(char) for char in self.str]

    @property
    def __add__(self, value):
        if self.use_default:
            return super().__add__(value)
        else:
            if isinstance(value, int):
                self.str += chr(value)
            elif isinstance(value, str):
                self.str += value
            else:
                raise TypeError(
                    f"unsupported operand type(s) for +: istr and {type(value)}"
                )
            return istr(self.str)


class Calc:
    def __init__(self, num: Union[int, float, dint]):
        self.num = num

    def __add__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num + value

    def __sub__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num - value

    def __mul__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num * value

    def __truediv__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num / value

    def __floordiv__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num // value

    def __mod__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num % value

    def __pow__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num**value

    def __lshift__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num << value

    def __rshift__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num >> value

    def __and__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num & value

    def __xor__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num ^ value

    def __or__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return self.num | value

    def __radd__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value + self.num

    def __rsub__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value - self.num

    def __rmul__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value * self.num

    def __rtruediv__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value / self.num

    def __rfloordiv__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value // self.num

    def __rmod__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value % self.num

    def __rpow__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value**self.num

    def __rlshift__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value << self.num

    def __rrshift__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value >> self.num

    def __rand__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value & self.num

    def __rxor__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value ^ self.num

    def __ror__(self, value: Union[int, float, dint]) -> Union[int, float, dint]:
        return value | self.num


class Div0Int(dint):
    def __truediv__(self, other):
        if other == 0:
            return float("inf")
        return super().__truediv__(other)

    def __floordiv__(self, other):
        if other == 0:
            return float("inf")
        return super().__floordiv__(other)


class NotCaseInsensitiveStr(istr):
    def __eq__(self, other: str):
        if self.str.lower() == other.lower():
            return True
        else:
            return False


Calculator: TypeAlias = Calc

del override, TypeAlias, Union
