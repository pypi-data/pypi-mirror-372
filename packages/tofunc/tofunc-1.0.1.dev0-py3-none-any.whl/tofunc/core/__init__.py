import functools
import types
from typing import *

__all__ = ["tofunc"]


def tofunc(old: Callable, /) -> types.FunctionType:
    def new(*args: Any, **kwargs: Any) -> Any:
        return old(*args, **kwargs)

    ans: types.FunctionType
    try:
        ans = functools.wraps(old)(new)
    except:
        ans = new
    return ans
