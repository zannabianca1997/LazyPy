from typing import Callable

from Validate import Invalidable, Cause


class InvalidableMethod(Invalidable):
    """A method that can be switched off"""
    __slots__ = ["__call__"]

    def __init__(self, method: Callable):
        super().__init__()
        self.__call__ = method

    def invalidate(self, cause: Cause):
        self.__call__ = lambda *args, **kwargs: None  # from now on the object won't do anything
        super().invalidate(cause)