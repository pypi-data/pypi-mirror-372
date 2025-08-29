from itertools import *
from functools import reduce
from typing import Iterable, Callable


def create_generator(values: list):
    return (i for i in values)


def create_generators(*values):
    return (i for i in values)


class IteratorRange:
    def __init__(self, start: int, end: int = None, step: int = None):
        self.start = start if end is not None else 0
        self.end = end if end is not None else start
        self.step = step if step is not None else 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.start >= self.end:
            raise StopIteration
        else:
            value = self.start
            self.start += self.step
            return value


class IteratorCalculator:
    def __init__(self, num):
        self.number = num

    def __iter__(self):
        return self

    def __next__(self):
        if self.number == 0:
            raise StopIteration
        self.number -= 1
        return self.number

    def change_number(self, func, value):
        self.number = func(self.number, value)
        return self.number

    def get_number(self):
        return self.number

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return self.number

    def __repr__(self):
        return f"IteratorCalculator({self.number})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        out_list = self.number + value
        o = IteratorCalculator(out_list)
        return o

    def __sub__(self, value):
        out_list = self.number - value
        o = IteratorCalculator(out_list)
        return o

    def __mul__(self, value):
        out_list = self.number * value
        o = IteratorCalculator(out_list)
        return o

    def __truediv__(self, value):
        out_list = self.number / value
        o = IteratorCalculator(out_list)
        return o

    def __floordiv__(self, value):
        out_list = self.number // value
        o = IteratorCalculator(out_list)
        return o

    def __mod__(self, value):
        out_list = self.number % value
        o = IteratorCalculator(out_list)
        return o

    def __pow__(self, value):
        out_list = self.number**value
        o = IteratorCalculator(out_list)
        return o

    def __lshift__(self, value):
        out_list = self.number << value
        o = IteratorCalculator(out_list)
        return o

    def __rshift__(self, value):
        out_list = self.number >> value
        o = IteratorCalculator(out_list)
        return o

    def __and__(self, value):
        out_list = self.number & value
        o = IteratorCalculator(out_list)
        return o

    def __xor__(self, value):
        out_list = self.number ^ value
        o = IteratorCalculator(out_list)
        return o

    def __or__(self, value):
        out_list = self.number | value
        o = IteratorCalculator(out_list)
        return o

    def __radd__(self, value):
        self.number += value
        return self

    def __rsub__(self, value):
        self.number -= value
        return self

    def __rmul__(self, value):
        self.number *= value
        return self

    def __rtruediv__(self, value):
        self.number /= value
        return self

    def __rfloordiv__(self, value):
        self.number //= value
        return self

    def __rmod__(self, value):
        self.number %= value
        return self

    def __rpow__(self, value):
        self.number **= value
        return self

    def __rlshift__(self, value):
        self.number <<= value
        return self

    def __rrshift__(self, value):
        self.number >>= value
        return self

    def __rand__(self, value):
        self.number &= value
        return self

    def __rxor__(self, value):
        self.number ^= value
        return self

    def __ror__(self, value):
        self.number |= value
        return self


class SampleIterator:
    def __init__(self, list):
        self.list = (i for i in list)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.list)


Iterator = SampleIterator

del Iterable, Callable
