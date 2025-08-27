import enum
import functools
import itertools
import tomllib
import unittest
from importlib import resources
from typing import *

from iterprod import core


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str = resources.read_text("iterprod.tests", "testdata.toml")
        data: dict = tomllib.loads(text)
        return data


class Test1984(unittest.TestCase):
    def go(
        self: Self,
        name: str,
        /,
        *,
        iterables: list[Iterable],
        **kwargs: Any,
    ) -> None:
        msg: str = "go %r" % name
        answer: list = list(core.iterprod(*iterables, **kwargs))
        solution: list = list(itertools.product(*iterables, **kwargs))
        self.maxDiff = None
        self.assertEqual(answer, solution, msg=msg)

    def test_0(self: Self) -> None:
        n: str
        q: dict
        for n, q in Util.util.data["go"].items():
            self.go(n, **q)


if __name__ == "__main__":
    unittest.main()
