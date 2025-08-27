import pandas as pd
import torch
from advancedlib import math


class List(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def average(self):
        return sum(self) / len(self)

    def median(self):
        n = len(self)
        s = sorted(self)
        return (s[n // 2] + s[~n // 2]) / 2 if n % 2 else s[n // 2]

    def mode(self):
        return max(set(self), key=self.count)

    def variance(self):
        n = len(self)
        mean = sum(self) / n
        return sum((x - mean) ** 2 for x in self) / n

    def std(self):
        return (self.variance()) ** 0.5

    def min(self):
        return min(self)

    def max(self):
        return max(self)

    def sum(self):
        return sum(self)

    def unique(self):
        return list(set(self))
