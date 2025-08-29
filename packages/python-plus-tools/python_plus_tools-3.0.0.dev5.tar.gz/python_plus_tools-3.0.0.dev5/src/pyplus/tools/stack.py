from queue import Queue, SimpleQueue
from collections import deque
from typing import TypeAlias, List
from advancedlib.itertools import IteratorCalculator, IteratorRange, SampleIterator


class FIFOStack:
    def __init__(self):
        self.stacks = []

    def put(self, items):
        self.stacks.append(items)

    def push(self):
        return self.stacks.pop(0)

    def get(self):
        return self.push()

    @property
    def is_empty(self):
        return len(self.stacks) == 0

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        out_list = self.stacks.append(value)
        o = FIFOStack()
        o.stacks = out_list
        return o


class ThreadFIFOStack(Queue):
    def push(self, items):
        self.stacks.append(items)

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()


class LIFOStack:
    def __init__(self):
        self.stacks = []

    def put(self, items):
        self.stacks.append(items)

    def push(self):
        return self.stacks.pop()

    def get(self):
        return self.push()

    @property
    def is_empty(self):
        return len(self.stacks) == 0

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        out_list = self.stacks.append(value)
        o = FIFOStack()
        o.stacks = out_list
        return o


class ThreadLIFOStack(SimpleQueue):
    def push(self, items):
        self.stacks.append(items)

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()


StackType: List[type] = [FIFOStack, LIFOStack]

Stack: TypeAlias = LIFOStack

DefaultStack: TypeAlias = LIFOStack
DefaultPipe: TypeAlias = FIFOStack
Stack, Pipe = DefaultStack, DefaultPipe

LIFO, FIFO = LIFOStack, FIFOStack


def set_default_stack(stack_type: type):
    global Stack, DefaultStack

    if stack_type in StackType:
        Stack, DefaultStack = stack_type, stack_type
    else:
        raise ValueError(f"Invalid stack type: {type(stack_type)}")


def set_default_pipe(pipe_type: type):
    global Pipe, DefaultPipe
    if pipe_type in StackType:
        Pipe, DefaultPipe = pipe_type, pipe_type
    else:
        raise ValueError(f"Invalid pipe type: {type(pipe_type)}")


del TypeAlias, List
