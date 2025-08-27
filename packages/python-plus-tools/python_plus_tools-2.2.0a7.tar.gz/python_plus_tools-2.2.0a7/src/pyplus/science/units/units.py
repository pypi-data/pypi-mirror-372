from abc import ABC, abstractclassmethod
import datetime
from typing import Union, TypeAlias, List, Dict, Callable, Literal
from typing import NamedTuple as ABCPoint
from collections import namedtuple as NamedPoint
from typing_extensions import override
import operator

UnitClass: TypeAlias = Union[List[Union[int, str]], "Unit"]

OPEN = True
CLOSE = False

(
    CONVERT,
    SYNC,
    SET_UNIT,
    SET_ONE,
    CHANGE_UNIT,
    OPERATOR,
    SET_UNIT,
    SET_NUMBER,
    ADD,
    SUB,
    MUL,
    DIV,
    TRUEDIV,
    FLOORDIV,
    MOD,
    DIVMOD,
    POW,
    LSHIFT,
    RSHIFT,
    AND,
    XOR,
    OR,
    RLSHIFT,
    RRSHIFT,
) = range(24)

all_command = [
    "CONVERT",
    "SYNC",
    "SET_UNIT",
    "SET_ONE",
    "CHANGE_UNIT",
    "OPERATOR",
    "SET_UNIT",
    "SET_NUMBER",
    "ADD",
    "SUB",
    "MUL",
    "DIV",
    "TRUEDIV",
    "FLOORDIV",
    "MOD",
    "POW",
    "LSHIFT",
    "RSHIFT",
    "AND",
    "XOR",
    "OR",
    "RLSHIFT",
    "RRSHIFT",
]

__all__ = all_command + [
    "BaseUnit",
    "Unit",
    "ABCUnit",
    "Line",
    "Area",
    "Volume",
    "Capacity",
    "Duration",
    "Version",
    "datetime",
    "Points",
    "NoInputTypeUnit",
    "UnitWeight",
    "Weight",
    "Length",
    "UnitPerUnit",
    "OPEN",
    "CLOSE",
    "ABCPoint",
    "NamedPoint",
]


class BaseUnit(object):
    def __init__(self, unit: str, type: str = ""):
        self.type = type
        self.unit = unit

    def __str__(self):
        return self.unit

    def __repr__(self):
        return self.unit

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.unit == other.unit
        else:
            raise TypeError("value '" + str(other) + "' is Not same type")

    def __ne__(self, value):
        return not self.__eq__(value)

    def __hash__(self):
        return hash((self.unit, self.type))

    def __bool__(self):
        return bool(self.unit)

    def __iter__(self):
        return iter([self.type, self.unit])

    def __getitem__(self, index):
        return [self.type, self.unit][index]

    def __setitem__(self, index, value):
        if index == 0:
            self.type = value
        elif index == 1:
            self.unit = value
        else:
            raise IndexError("list index out of range")


class Unit(BaseUnit):
    """
    The unit class.It can use in science calculate.

    :Example:
    >>> Unit(1,'a')
    '1a'

    :param int number: Your Unit number.
    :param str unit: Your Unit unit.
    :param str = "" type: Your Unit type.
    """

    (
        CONVERT,
        SYNC,
        SET_UNIT,
        SET_ONE,
        CHANGE_UNIT,
        OPERATOR,
        SET_UNIT,
        SET_NUMBER,
        ADD,
        SUB,
        MUL,
        DIV,
        TRUEDIV,
        FLOORDIV,
        MOD,
        DIVMOD,
        POW,
        LSHIFT,
        RSHIFT,
        AND,
        XOR,
        OR,
        RLSHIFT,
        RRSHIFT,
    ) = range(24)

    conversion_list: Dict[str, int] = {}

    __slots__ = [
        "number",
        "unit",
        "data",
        "unit_list",
        "unit_conversion",
        "type_custom",
        "type",
    ]

    def __init__(
        self, number: int, unit: str, type: str = "", type_custom: bool = True
    ):
        super().__init__(unit, type)

        self.number = number
        self.data = [self.number, self.unit]
        self.unit_list: List[str] = []
        self.unit_conversion: List[int] = []
        self.type_custom: bool = type_custom
        for k, v in self.conversion_list.items():
            self.unit_list.append(k)
            self.unit_conversion.append(v)

    def convert(self, end_unit: str):
        """
        Convert your unit.
        Before use it,please set the convert list.

        :Example:
        >>> a = Unit(1,'a')
        >>> a.set_con(a = 1, b = 100)
        >>> a.convert('b')
        '0.01b'

        :param str end_unit: The unit you want to convert into.
        :return: Convert the unit.
        :rtype: Unit.
        """
        number = self.number * (
            self.conversion_list[self.unit.lower()]
            / self.conversion_list[end_unit.lower()]
        )
        unit = end_unit
        return self.__create_new(number, unit)

    def _sync_converion_list(self, other: "Unit"):
        """
        If two Unit's type is same,the other's convert list is self convert list.

        :raises TypeError: You input is not a Unit class.
        """
        if isinstance(other, self.__class__):
            if self.type.lower() == other.type.lower():
                other.conversion_list = self.conversion_list
        else:
            raise TypeError("value '" + str(other) + "' is Not same type")

    def set_con(self, **list):
        "Set the convert list."
        self.conversion_list = {}
        self.unit_conversion = []
        self.unit_list = []
        for k, v in list.items():
            self.conversion_list[k] = v
            self.unit_conversion.append(v)
            self.unit_list.append(k)

    def append_con(self, **list):
        "Append the convert list."
        for k, v in list.items():
            self.conversion_list[k] = v
            self.unit_conversion.append(v)
            self.unit_list.append(k)

    def delete_con(self, keys: str):
        "Delete the convert list."
        indexs = self.unit_list.index(keys)
        del self.conversion_list[keys]
        del self.unit_list[indexs]
        del self.unit_conversion[indexs]

    def set_attr(self, value: UnitClass, conversion_unit: bool = CLOSE):
        """
        Set the Unit is input unit.

        :Example:
        >>> a = Unit(1,'a')
        >>> b = Unit(1,'b')
        >>> a.set_con(a = 1, b = 100)
        >>> a.set_attr(b)
        '100a'
        >>> a.set_attr(b,True)
        '1b'
        >>> a.set_attr([20,'a'])
        '20a'

        :param list[int,str] | Unit class value: Unit you want to set.
        :param bool = False convert: If you want to set the unit too,set this variable True.
        :return: The input Unit class
        :rtype: Unit
        """
        if isinstance(value, self.__class__):
            self._sync_converion_list(value)
            number = value.number
            if conversion_unit:
                unit = value.unit
            else:
                unit = self.unit
            return self.__create_new(number, unit)
        elif isinstance(value, list):
            if value[1].lower() in self.conversion_list:
                unit = value[1]
                number = value[0]
                return self.__create_new(number, unit)
            else:
                raise KeyError("key'" + self.unit + "'is not in this class")
        else:
            raise TypeError(
                "value '"
                + str(value)
                + "' is"
                + str(type(value))
                + ", not Unit or list."
            )

    def setone(self, unit: str):
        """
        Set the unit is 1, else correspond change.

        :param str unit: Unit you want to convert.
        """
        temp_dict = self.conversion_list
        for k, v in self.conversion_list.items():
            temp_dict[k] = v / self.conversion_list[unit]
        self.conversion_list = temp_dict

    def __create_new(self, num: int, unit: str):
        """
        If you create a Unit class when inherit is Unit(recommed use this unit when you create create a Unit class).
        Clone a new unit.

        :return: A new Unit class.
        :rtype: Unit
        """
        if self.type_custom:
            n = self.__class__(num, unit, self.type)
        else:
            n = self.__class__(num, unit)

        self._sync_converion_list(n)
        return n

    def change_attr(self, func: Callable, value: UnitClass):
        """
        Change the Unit.

        :Example:
        >>> a = Unit(1,'a')
        >>> b = Unit(1,'b')
        >>> a.set_con(a = 1, b = 100)
        >>> a.change_attr(operator.add,b)
        '101a'
        >>> a.change_attr(operator.add,[20,'a'])
        '21a'

        :param function func: The control function.It is in operator.
        :param list[int,str] | Unit class value: The change value.
        :return: The changed Unit class
        :rtype: Unit
        """
        if isinstance(value, self.__class__):
            self._sync_converion_list(value)
            number = func(self.number, value.convert(self.unit).number)
            return self.__create_new(number, self.unit)
        elif isinstance(value, list):
            if value[1].lower() in self.conversion_list:
                value[0] *= (
                    self.conversion_list[value[1]] / self.conversion_list[self.unit]
                )
                number = func(self.number, value[0])
                return self.__create_new(number, self.unit)
            else:
                raise KeyError("key'" + value[1] + "'is not in this class")
        else:
            raise TypeError(
                "value '"
                + str(value)
                + "' is"
                + str(type(value))
                + ", not Unit or list."
            )

    def operator(self, func: Callable, value: UnitClass) -> bool:
        """
        Operator the unit.

        :Example:
        >>> a = Unit(1,'a')
        >>> b = Unit(1,'b')
        >>> a.set_con(a = 1, b = 100)
        >>> a.operator(operator.gt, b)
        False
        >>> a.operator(operator.le, [20, 'a'])
        True

        :param function func: The control function.It is in operator.
        :param list[int,str] | Unit class value: The change value.
        :return: The operator Unit class result.
        :rtype: bool
        """
        if isinstance(value, self.__class__):
            self._sync_converion_list(value)
            op = func(self.number, value.convert(self.unit).number)
        elif isinstance(value, list):
            if value[1].lower() in self.conversion_list:
                value[0] *= (
                    self.conversion_list[value[1]] / self.conversion_list[self.unit]
                )
                op = func(self.number, value[0])
            else:
                raise KeyError("key'" + value[1] + "'is not in this class")
        else:
            raise TypeError(
                "value '"
                + str(value)
                + "' is"
                + str(type(value))
                + ", not Unit or list."
            )
        return op

    @property
    def attributes(self):
        return f"{'attributes': -^30}\nnum = {self.number}\nunit = {self.unit}\ntype = {self.type}\nconversion = {self.conversion_list}"

    def set_num(self, other: Union[int, "Unit"]):
        """
        Set the number.
        """
        if isinstance(other, self.__class__):
            number = other.number
        elif isinstance(other, int):
            number = other
        else:
            raise TypeError(
                "value '"
                + str(other)
                + "' is"
                + str(type(other))
                + ", not Unit or int."
            )
        return self.__create_new(number, self.unit)

    def set_unit(self, other: Union[str, "Unit"]):
        """
        Value can Unit too.
        Set the unit.
        """
        save_unit = self.unit
        if isinstance(other, self.__class__):
            unit = other.unit
        elif isinstance(other, str):
            unit = other
        else:
            raise TypeError(
                "value '"
                + str(other)
                + "' is"
                + str(type(other))
                + ", not Unit or str."
            )
        if self.unit.lower() not in self.conversion_list:
            self.unit = save_unit
            raise KeyError("key '" + self.unit + "'not in convert list.")
        return self.__create_new(self.number, unit)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        if index == 0:
            self.number = value
        elif index == 1:
            self.unit = value
        else:
            raise IndexError("list index out of range")

    def __call__(self, command, *value):
        try:
            if command == CONVERT:
                return self.convert(value[0])
            elif command == SYNC:
                self._sync_converion_list(value[0])
            elif command == SET_UNIT:
                return self.set_unit(value[0])
            elif command == SET_ONE:
                return self.setone(value[0])
            elif command == CHANGE_UNIT:
                return self.change_attr(value[0], value[1])
            elif command == OPERATOR:
                return self.operator(value[0], value[1])
            elif command == SET_NUMBER:
                return self.set_num(value[0])
            elif command == ADD:
                return self.__add__(value[0])
            elif command == SUB:
                return self.__sub__(value[0])
            elif command == MUL:
                return self.__mul__(value[0])
            elif command == DIV:
                return self.__truediv__(value[0])
            elif command == FLOORDIV:
                return self.__floordiv__(value[0])
            elif command == MOD:
                return self.__mod__(value[0])
            elif command == DIVMOD:
                return self.__divmod__(value[0])
            elif command == POW:
                return self.__pow__(value[0])
            elif command == LSHIFT:
                return self.__lshift__(value[0])
            elif command == RSHIFT:
                return self.__rshift__(value[0])
            elif command == AND:
                return self.__and__(value[0])
            elif command == XOR:
                return self.__xor__(value[0])
            elif command == OR:
                return self.__or__(value[0])
            elif command == RLSHIFT:
                return self.__rlshift__(value[0])
            elif command == RRSHIFT:
                return self.__rrshift__(value[0])
            else:
                raise ValueError("command not found")
        except IndexError:
            raise ValueError(f"This command need more value.(got {len(value)})")

    def __add__(self, value):
        return self.change_attr(operator.add, value)

    def __sub__(self, value):
        return self.change_attr(operator.sub, value)

    def __mul__(self, value):
        number = self.number * value
        return self.__create_new(number, self.unit)

    def __truediv__(self, value):
        number = self.number / value
        return self.__create_new(number, self.unit)

    def __floordiv__(self, value):
        number = self.number // value
        return self.__create_new(number, self.unit)

    def __divmod__(self, value):
        return self.change_attr(divmod, value)

    def __pow__(self, value, modulo=None):
        if isinstance(value, self.__class__):
            self._sync_converion_list(value)
            number = pow(self.number, value.convert(self.unit).number, modulo)
            return self.__create_new(number, self.unit)
        elif isinstance(value, list):
            if value[1].lower() in self.conversion_list:
                value[0] *= (
                    self.conversion_list[value[1]] / self.conversion_list[self.unit]
                )
                number = pow(self.number, value[0], modulo)
                return self.__create_new(number, self.unit)
            else:
                raise KeyError("key'" + value[1] + "'is not in this class")
        else:
            raise TypeError(
                "value '"
                + str(value)
                + "' is"
                + str(type(value))
                + ", not Unit or list."
            )

    def __setitem__(self, index, value):
        if index == 0:
            self.set_num(value)
        elif index == 1:
            self.set_unit(value)
        else:
            raise IndexError("list index out of range")

    def __round__(self, n=None):
        return self.__create_new(round(self.number, n), self.unit)

    def __floor__(self):
        import math

        return self.__create_new(math.floor(self.number), self.unit)

    def __ceil__(self):
        import math

        return self.__create_new(math.ceil(self.number), self.unit)

    def __trunc__(self):
        import math

        return self.__create_new(math.trunc(self.number), self.unit)

    def __mod__(self, value):
        self.change_attr(operator.mod, value)

    def __and__(self, value):
        self.change_attr(operator.and_, value)

    def __xor__(self, value):
        self.change_attr(operator.xor, value)

    def __or__(self, value):
        self.change_attr(operator.or_, value)

    def __invert__(self):
        self.change_attr(operator.invert, None)

    def __radd__(self, value: list):
        return self.__add__(value)

    def __rsub__(self, value: list):
        return self.__sub__(value)

    def __rmul__(self, value):
        return self.__mul__(value)

    def __rtruediv__(self, value):
        return self.__truediv__(value)

    def __rfloordiv__(self, value):
        return self.__floordiv__(value)

    def __rpow__(self, value):
        return self.__pow__(value)

    def __rmod__(self, value):
        return self.__mod__(value)

    def __rand__(self, value):
        return self.__and__(value)

    def __rxor__(self, value):
        return self.__xor__(value)

    def __ror__(self, value):
        return self.__or__(value)

    def __lshift__(self, other):
        """
        Value can Unit too.
        If num is Unit, set the self unit the other unit, same as set_unit(other)
        If num is int, set the unit left the other.
        """
        if isinstance(other, self.__class__):
            unit = other.unit
        elif isinstance(other, int):
            unit = self.unit_list[self.unit_list.index(self.unit) - other]
        else:
            raise TypeError(
                "value '"
                + str(other)
                + "' is"
                + str(type(other))
                + ", not Unit or int."
            )
        return self.__create_new(self.number, unit)

    def __rlshift__(self, other):
        """
        Value can Unit too.
        If num is Unit, set the self unit the other unit, same as set_unit(other)
        If num is int, set the unit left the other.
        """
        if isinstance(other, int):
            return other << self.number
        else:
            raise TypeError(
                "value '"
                + str(other)
                + "' is"
                + str(type(other))
                + ", not Unit or int."
            )

    def __rshift__(self, other):
        """
        Value can Unit too.
        If num is Unit, set the self unit the other unit, same as other.set_unit(self)
        If num is int, set the unit right the other.
        """
        if isinstance(other, self.__class__):
            other.set_unit(self)
        elif isinstance(other, int):
            unit = self.unit_list[self.unit_list.index(self.unit) + other]
        else:
            raise TypeError(
                "value '"
                + str(other)
                + "' is"
                + str(type(other))
                + ", not Unit or int."
            )
        return self.__create_new(self.number, unit)

    def __rrshift__(self, other):
        """
        Value can Unit too.
        If num is Unit, set the self unit the other unit, same as other.set_unit(self)
        If num is int, set the unit right the other.
        """
        if isinstance(other, int):
            return other >> self.number
        else:
            raise TypeError(
                "value '" + str(other) + "' is" + str(type(other)) + ", not int."
            )

    def __eq__(self, value: list):
        return self.operator(operator.eq, value)

    def __ne__(self, value: list):
        return self.operator(operator.ne, value)

    def __lt__(self, value: list):
        return self.operator(operator.lt, value)

    def __gt__(self, value: list):
        return self.operator(operator.gt, value)

    def __le__(self, value: list):
        return self.operator(operator.le, value)

    def __ge__(self, value: list):
        return self.operator(operator.ge, value)

    def __neg__(self):
        return self.__create_new(-self.number, self.unit)

    def __pos__(self):
        return self.__create_new(self.number, self.unit)

    def __str__(self):
        return str(self.number) + self.unit

    def __repr__(self):
        return str(self.number) + self.unit

    def __hash__(self):
        return hash(tuple(self.data))

    def __bytes__(self):
        return bytes([self.number] + [ord(c) for c in self.unit])

    def __format__(self, format_spec):
        if format_spec == "m":
            return str(self.number) + "" + self.unit
        elif format_spec == "s":
            return str(self.number) + " " + self.unit
        elif format_spec == "c":
            return str(self.number) + "," + self.unit
        elif format_spec == "n":
            return str(self.number)
        elif format_spec == "f":
            return f"{self.number:.2f}" + self.unit
        elif format_spec == "u":
            return self.unit
        elif format_spec == "r":
            return self.unit + str(self.number)

    def __bool__(self):
        return bool(self.number)

    def __getattr__(self, name):
        raise AttributeError(
            f"{self.__class__.__name__} object has no attribute '{name}'"
        )

    def __contains__(self, item):
        return item in self.conversion_list

    def __len__(self):
        return len(self.conversion_list)

    def __length_hint__(self):
        return 2

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ABCUnit(ABC, Unit):
    """
    Simply to create a customised UnitClass.

    This class must define a method `__create_new`.

    This class cannot be called directly.If you need to use it,you must inherit this type.
    """

    def __init__(self, number, unit, type=""):
        super().__init__(number, unit, type)

    @override
    @abstractclassmethod
    def __create_new(self, num, unit):
        """This method must be defined."""
        return super().__create_new(num, unit)


class NoInputTypeUnit(Unit):
    """
    Simply to create a UnitClass.
    """

    def __init__(self, number, unit):
        super().__init__(number, unit, None, False)


class Line(Unit):
    conversion_list = {
        "nm": 1 / 1000**2,
        "um": 1 / 1000,
        "mm": 1,
        "cm": 10,
        "dm": 100,
        "m": 1000,
        "km": 1000 * 1000,
        "AU": 149_597_870.7 * 1000**2,
        "ly": 63241.1 * 149_597_870.7 * 1000**2,
        "pc": 206264.8 * 149_597_870.7 * 1000**2,
        "mpc": 100_0000 * 206264.8 * 149_597_870.7 * 1000**2,
        "in": 2540,
        "ft": 12 * 2540,
        "yd": 36 * 2540,
        "mi": 63660 * 2540,
        "nmi": 1.852 * 1000**2,
    }

    def __init__(self, number, unit):
        super().__init__(number, unit, "line", False)
        if self.unit.lower() not in self.conversion_list:
            raise KeyError("key'" + self.unit + "'is not in this class")


Length: TypeAlias = Line


class Area(Unit):
    conversion_list = {
        "nm2": 1 / 1000**4,
        "um2": 1 / 1000**2,
        "mm2": 1,
        "cm2": 100,
        "dm2": 10000,
        "m2": 10000 * 100,
        "are": 10000**2,
        "ha": 10000**2 * 100,
        "km2": 10000**3,
        "in2": 2540**2,
        "ft2": (12 * 2540) ** 2,
        "mi2": (63660 * 2540) ** 2,
        "acre2": 4046_8564_22.4,
    }

    def __init__(self, number, unit):
        super().__init__(number, unit, "area", False)
        if self.unit.lower() not in self.conversion_list:
            raise KeyError("key'" + self.unit + "'is not in this class")

    def scale(self, value: int):
        self.number *= value**2
        return self

    @override
    def __mul__(self, value: int):
        assert isinstance(value, int)
        self.number *= value**2
        return self

    @override
    def __truediv__(self, value: int):
        assert isinstance(value, int)
        self.number /= value**2
        return self


class Volume(Unit):
    conversion_list = {
        "nm3": 1 / 1000**6,
        "um3": 1 / 1000**3,
        "mm3": 1,
        "cm3": 1000,
        "dm3": 1000**2,
        "m3": 1000**3,
        "km3": 1000**6,
        "in3": 2540**3,
        "ft3": (12 * 2540) ** 3,
        "mi3": (63660 * 2540) ** 3,
    }

    def __init__(self, number, unit):
        super().__init__(number, unit, "volume", False)
        if self.unit.lower() not in self.conversion_list:
            raise KeyError("key'" + self.unit + "'is not in this class")

    def scale(self, value: int):
        self.number *= value**3
        return self

    @override
    def __mul__(self, value: int):
        assert isinstance(value, int)
        self.number *= value**3
        return self

    @override
    def __truediv__(self, value: int):
        assert isinstance(value, int)
        self.number /= value**3
        return self

    @property
    def capacity(self) -> "Capacity":
        return Capacity(self.convert("dm3").number, "L")

    def weight(self, mass: "UnitWeight") -> "Weight":
        return Weight(
            self.convert(mass.unit.unit).number * mass.weight.unit, mass.weight.unit
        )


class Capacity(Unit):
    conversion_list = {
        "ml": 1,
        "l": 1000,
        "oz": 29.6,
        "dr": 29.6 * 0.125,
        "pt": 16 * 29.6,
        "tbsp": 14.8,
        "cup": 48 * 14.8,
        "gal": 128 * 29.6,
        "tsp": 14.8 / 3,
        "tb": 1000 * 14.8,
        "fl oz": 16 * 29.6,
        "pint": 16 * 29.6,
        "qt": 2 * 16 * 29.6,
        "gal US": 128 * 29.6,
        "tbs": 14.8,
        "fl oz US": 16 * 29.6,
        "pints US": 16 * 29.6,
        "qts US": 2 * 16 * 29.6,
    }

    def __init__(self, number, unit):
        super().__init__(number, unit, "capacity", False)
        if self.unit.lower() not in self.conversion_list:
            raise KeyError("key'" + self.unit + "'is not in this class")

    @property
    def volume(self) -> "Volume":
        return Volume(self.convert("L").number, "dm3")

    def weight(self, mass: "UnitWeight") -> "Weight":
        return Weight(
            self.convert(mass.unit.unit).number * mass.weight.number, mass.weight.unit
        )


class Duration(Unit):
    conversion_list = {
        "ms": 1,
        "s": 1000,
        "h": 60000,
        "d": 60000 * 24,
        "u": 60000 * 24 * 365 / 4,
        "y": 60000 * 24 * 365,
        "a": 60000 * 24 * 365 * 10,
        "c": 60000 * 24 * 365 * 100,
    }

    def __init__(self, number: int, unit: str):
        super().__init__(number, unit, "duration", False)
        if self.unit.lower() not in self.conversion_list:
            raise KeyError("key'" + self.unit + "'is not in this class")


class Weight(Unit):
    conversion_list = {
        "g": 1,
        "kg": 1000,
        "mg": 1 / 1000,
        "ug": 1 / 1000**2,
        "ng": 1 / 1000**3,
        "pg": 1 / 1000**4,
        "fg": 1 / 1000**5,
        "dg": 10,
        "cg": 100,
        "lb": 453.592,
        "oz": 28.3495,
        "dr": 28.3495 * 0.125,
        "pt": 16 * 28.3495,
        "tbsp": 14.17475,
        "cup": 48 * 14.17475,
        "gal": 128 * 28.3495,
        "tsp": 14.17475 / 3,
        "ton": 1000,
        "tonne": 1000,
        "slug": 14593.903,
    }

    def __init__(self, number: int, unit: str):
        super().__init__(number, unit, "weight", False)
        if self.unit.lower() not in self.conversion_list:
            raise KeyError("key'" + self.unit + "'is not in this class")


class UnitPerUnit:
    def __init__(self, unit1: Unit, unit2: Unit):
        self.unit1 = unit1
        self.unit2 = unit2


class UnitWeight(UnitPerUnit):
    def __init__(self, unit: Union[Capacity, Volume], weight: Weight):
        super().__init__(unit, weight)
        self.weight = weight
        self.unit = unit


class Time:
    def __init__(self):
        pass


class Version:
    """use to write project version."""

    def __init__(self, *version):
        self.version_list = [str(i) for i in version]
        self.version = ".".join(self.version_list)

    def __iter__(self):
        return iter(self.version_list)

    def __getitem__(self, index):
        return self.version_list[index]

    def __len__(self):
        return len(self.version_list)

    def __repr__(self):
        return self.version


class Points:
    __slots__ = ["dots"]

    def __init__(self, *dots):
        self.dots = dots

    @property
    def vec(self):
        return len(self.dots)

    def set_dot(self, *dots, D_same: Literal[True, False] = OPEN):
        if D_same and len(dots) != self.vec:
            raise ValueError(
                f"You are open the D_same.You input length must be equal to the length you set.(input {len(dots)},Set {self.vec})"
            )
        self.dots = dots
        return self

    def add_dot(self, dot: tuple[int]):
        self.dots += dot
        return self

    def __iter__(self):
        return iter(self.dots)

    def __getitem__(self, index):
        return self.dots[index]

    def __len__(self):
        return len(self.dots)

    def __repr__(self):
        return str(self.dots)

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        point = list(self.dots)
        if isinstance(value, tuple) or isinstance(value, Points):
            for i in range(len(self.dots)):
                try:
                    point[i] += value[i]
                except IndexError:
                    break
        else:
            raise TypeError(
                f"Points operator must use Points or tuple,not {type(value)}"
            )
        return Points(*tuple(point))

    def __sub__(self, value):
        point = list(self.dots)
        if isinstance(value, tuple) or isinstance(value, Points):
            for i in range(len(self.dots)):
                try:
                    point[i] -= value[i]
                except IndexError:
                    break
        else:
            raise TypeError(
                f"Points operator must use Points or tuple,not {type(value)}"
            )
        return Points(*tuple(point))

    def __mul__(self, value):
        point = list(self.dots)
        if isinstance(value, tuple) or isinstance(value, Points):
            for i in range(len(self.dots)):
                try:
                    point[i] *= value[i]
                except IndexError:
                    break
        elif isinstance(value, int):
            for i in range(len(self.dots)):
                try:
                    point[i] *= value
                except IndexError:
                    break
        else:
            raise TypeError(
                f"Points operator must use Points,tuple or int,not {type(value)}"
            )
        return Points(*tuple(point))

    def __truediv__(self, value):
        point = list(self.dots)
        if isinstance(value, tuple) or isinstance(value, Points):
            for i in range(len(self.dots)):
                try:
                    point[i] /= value[i]
                except IndexError:
                    break
        elif isinstance(value, int):
            for i in range(len(self.dots)):
                try:
                    point[i] /= value
                except IndexError:
                    break
        else:
            raise TypeError(
                f"Points operator must use Points,tuple or int,not {type(value)}"
            )
        return Points(*tuple(point))

    def __radd__(self, value):
        return self.__add__(value)

    def __rsub__(self, value):
        return self.__sub__(value)

    def __rmul__(self, value):
        return self.__mul__(value)

    def __rtruediv__(self, value):
        return self.__truediv__(value)

    def __neg__(self):
        dot = list(self.dots)
        for i in range(len(dot)):
            dot[i] = -dot[i]
        return Points(*tuple(dot))

    def __pos__(self):
        return Points(*self.dots)


del Union, abstractclassmethod, override, ABC, TypeAlias, Callable, List, Dict, Literal
