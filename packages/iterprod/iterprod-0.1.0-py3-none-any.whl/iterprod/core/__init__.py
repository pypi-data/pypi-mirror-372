import operator
from typing import *

__all__ = ["iterprod"]


def iterprod(*iterables: Iterable, repeat: SupportsIndex = 1) -> Generator:
    if repeat < 0:
        raise ValueError("repeat argument cannot be negative")
    pools: Iterable = map(tuple, iterables)
    pools = list(pools)
    pools *= repeat
    indeces: list = [0] * len(pools)
    lengths: tuple = tuple(map(len, pools))
    while True:
        yield tuple(map(operator.getitem, pools, indeces))
        try:
            incr(indeces, lengths)
        except IndexError:
            return


def incr(indeces: list, lengths: tuple) -> None:
    indeces[-1] += 1
    j: int = -1
    while True:
        if indeces[j] < lengths[j]:
            return
        indeces[j] = 0
        indeces[j - 1] += 1
        j -= 1
