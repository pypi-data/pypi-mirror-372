import functools
import types
import unittest
from typing import *

from tofunc import tofunc


class TestHello(unittest.TestCase):
    def test_hello(self: Self) -> None:
        def join(self: Self, b: Any = "beta", c: Any = "gamma") -> str:
            return "%s %s %s" % (self, b, c)

        class Foo: ...

        hello: functools.partial = functools.partial(join, c="hello")
        Foo.greet = hello
        self.assertEqual(Foo().greet("Alice"), "Alice beta hello")
        hello: types.FunctionType = tofunc(hello)
        Foo.greet = hello
        text: str = Foo().greet("Bob")
        self.assertTrue(text.endswith("Bob hello"))
        self.assertTrue("Foo" in text)


if __name__ == "__main__":
    unittest.main()
