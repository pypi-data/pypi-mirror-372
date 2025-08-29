from pyplus.science.units import Duration
from timeit import *
from time import *

MS = 1
SEC = 1000
SEC_TIME = Duration(1, "s")
MS_TIME = Duration(1, "ms")


class Clock:
    def __init__(self):
        self.time = 0
        self.stopped = False
        self.clock_type = None

    def down_start(self, msecs: int):
        from threading import Thread

        assert isinstance(msecs, int)
        self.clock_type = "down"
        self.stopped = False
        self.time = msecs / 1000

        def tick():
            while self.time > 0 and not self.stopped:
                self.time -= 0.001
                sleep(0.001)
                if self.time == 1:
                    self.clock_type = None

        Thread(target=tick).start()

    def restart(self):
        self.stopped = False
        if self.clock_type == "down":
            self.down_start(self.time)
        elif self.clock_type == "up":
            self.start()
        if self.time == 0:
            self.clock_type = None
            raise TimeoutError("this clock is not running.")

    def stop(self):
        self.stopped = True

    def clear(self):
        self.time = 0
        self.clock_type = None

    def start(self):
        from threading import Thread

        self.clock_type = "up"

        def tick():
            while self.time >= 0 and not self.stopped:
                self.time += 1
                sleep(0.001)
                if self.time == 0:
                    self.clock_type = None

        Thread(target=tick).start()

    def is_running(self):
        return self.clock_type is not None

    def get_time(self):
        return self.time + "ms"

    def get_time_s(self):
        return Duration(self.time / 1000, "s")

    def __str__(self):
        return f"{self.get_time_str()}ms"

    def __repr__(self):
        return self.__str__()

    def __int__(self):
        return self.get_time()

    def __float__(self):
        return self.get_time_s()

    def __add__(self, other):
        if isinstance(other, Clock):
            return Clock(self.time + other.time)
        elif isinstance(other, int):
            return Clock(self.time + other)
        elif isinstance(other, float):
            return Clock(self.time + other * 1000)
        elif isinstance(other, Duration):
            return Clock(self.time + other.conversion("ms").number)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: 'Clock' and '{type(other).__name__}'"
            )

    def __sub__(self, other):
        if isinstance(other, Clock):
            return Clock(self.time - other.time)
        elif isinstance(other, int):
            return Clock(self.time - other)
        elif isinstance(other, float):
            return Clock(self.time - other * 1000)
        elif isinstance(other, Duration):
            return Clock(self.time - other.conversion("ms").number)
        else:
            raise TypeError(
                f"unsupported operand type(s) for -: 'Clock' and '{type(other).__name__}'"
            )

    def __mul__(self, other):
        if isinstance(other, int):
            return Clock(self.time * other)
        elif isinstance(other, float):
            return Clock(self.time * other * 1000)
        elif isinstance(other, Duration):
            return Clock(self.time * other.conversion("ms").number)
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: 'Clock' and '{type(other).__name__}'"
            )

    def __truediv__(self, other):
        if isinstance(other, int):
            return Clock(self.time / other)
        elif isinstance(other, float):
            return Clock(self.time / other * 1000)
        elif isinstance(other, Duration):
            return Clock(self.time / other.conversion("ms").number)
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: 'Clock' and '{type(other).__name__}'"
            )

    def __lt__(self, other):
        if isinstance(other, Clock):
            return self.time < other.time
        elif isinstance(other, int):
            return self.time < other
        elif isinstance(other, float):
            return self.time < other * 1000
        elif isinstance(other, Duration):
            return self.time < other.conversion("ms").number
        else:
            raise TypeError(
                f"unsupported operand type(s) for <: 'Clock' and '{type(other).__name__}'"
            )

    def __le__(self, other):
        if isinstance(other, Clock):
            return self.time <= other.time
        elif isinstance(other, int):
            return self.time <= other
        elif isinstance(other, float):
            return self.time <= other * 1000
        elif isinstance(other, Duration):
            return self.time <= other.conversion("ms").number
        else:
            raise TypeError(
                f"unsupported operand type(s) for <=: 'Clock' and '{type(other).__name__}'"
            )

    def __eq__(self, other):
        if isinstance(other, Clock):
            return self.time == other.time
        elif isinstance(other, int):
            return self.time == other
        elif isinstance(other, float):
            return self.time == other * 1000
        elif isinstance(other, Duration):
            return self.time == other.conversion("ms").number
        else:
            raise TypeError(
                f"unsupported operand type(s) for ==: 'Clock' and '{type(other).__name__}'"
            )

    def __ne__(self, other):
        if isinstance(other, Clock):
            return self.time != other.time
        elif isinstance(other, int):
            return self.time != other
        elif isinstance(other, float):
            return self.time != other * 1000
        elif isinstance(other, Duration):
            return self.time != other.conversion("ms").number
        else:
            raise TypeError(
                f"unsupported operand type(s) for !=: 'Clock' and '{type(other).__name__}'"
            )

    def __gt__(self, other):
        if isinstance(other, Clock):
            return self.time > other.time
        elif isinstance(other, int):
            return self.time > other
        elif isinstance(other, float):
            return self.time > other * 1000
        elif isinstance(other, Duration):
            return self.time > other.conversion("ms").number
        else:
            raise TypeError(
                f"unsupported operand type(s) for >: 'Clock' and '{type(other).__name__}'"
            )

    def __ge__(self, other):
        if isinstance(other, Clock):
            return self.time >= other.time
        elif isinstance(other, int):
            return self.time >= other
        elif isinstance(other, float):
            return self.time >= other * 1000
        elif isinstance(other, Duration):
            return self.time >= other.conversion("ms").number
        else:
            raise TypeError(
                f"unsupported operand type(s) for >=: 'Clock' and '{type(other).__name__}'"
            )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return self.time
