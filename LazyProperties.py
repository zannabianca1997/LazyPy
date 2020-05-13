from itertools import chain
from typing import Union, Any, Optional, Callable, Iterable, Dict

from .Require import Requirable
from .ExtendedRequire import StrRequirer
from .Validate import Cause


class LazyProperty(property):
    """A lazily evaluated property. It's value will be cached and recalculated only when needed.
    Can depend on other LazyProperty. If they are invalidate, for example by setting them, this is invalidated too.
    Some requirement can be expressed as string. In that case they will be evaluated at runtime, with self = obj"""
    #__slots__ = ["name", "cache_name", "requirements"]
    CACHE_PREFIX = "_cache_"

    def __init__(self, name:str, fget: Optional[Callable[[Any], Any]] = None, fset: Optional[Callable[[Any, Any], None]] = None,
                 fdel: Optional[Callable[[Any], None]] = None, doc: Optional[str] = None,
                 requirements: Optional[Iterable[Union[Requirable, str]]] = ()) -> None:
        super().__init__(fget, fset, fdel, doc)
        self.name = name
        self.cache_name = self.CACHE_PREFIX + name
        self.requirements = requirements

    class LazyPropertyCache(StrRequirer):
        """The cache for this property"""
        __slots__ = ["value"]

        def __init__(self, requirements: Optional[Iterable[Union[Requirable, str]]] = (),
                     eval_vars: Optional[Dict[str, Any]] = None):
            super().__init__(requirements, eval_vars)
            self.value = None


        class SettedValue(Cause):
            __slots__ = ["obj"]

            def __init__(self, obj: Any):
                self.obj = obj

            def __str__(self):
                return f"fset was called on {self.obj}"

            def __repr__(self):
                return f"{type(self)}(obj={self.obj})"

        class DeletedProperty(Cause):
            __slots__ = ["obj"]

            def __init__(self, obj: Any):
                self.obj = obj

            def __str__(self):
                return f"fdel was called on {self.obj}"

            def __repr__(self):
                return f"{type(self)}(obj={self.obj})"

        def __repr__(self):
            return repr({"cache": self.value, "valid": self.valid})

    def get_cache(self, obj: Any) -> LazyPropertyCache:
        """Get the cache in obj. If there isn't, it's created"""
        try:
            cache = getattr(obj, self.cache_name)
        except AttributeError:  # va creata
            cache = self.LazyPropertyCache(self.requirements, {"self": obj})
            setattr(obj, self.cache_name, cache)
        return cache


    def __get__(self, obj: Any, type: Optional[type] = None) -> Any:
        if obj is None:  # access through a class
            return self
        if self.fget is None:  # ungettable lazy class? wut. Anyway it should emulate property so...
            raise AttributeError("unreadable attribute")
        cache = self.get_cache(obj)
        if not cache.valid:  # redo the calculations only when the cache is invalid
            cache.validate()  # require all dependencies.
            cache.value = self.fget(obj)  # calculating the value
        return cache

    def __set__(self, obj: Any, value: Any) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)
        self.get_cache(obj).invalidate(self.LazyPropertyCache.SettedValue(obj))  # invalidate the cache

    def __delete__(self, obj: Any) -> None:
        if hasattr(obj, self.cache_name):  # deleting the cache
            getattr(obj, self.cache_name).invalidate(self.LazyPropertyCache.DeletedProperty(obj))
            delattr(obj, self.cache_name)
        if self.fdel is not None:  # deleting the eventual object
            self.fdel(obj)

    def getter(self, fget: Callable[[Any], Any]) -> "LazyProperty":
        return type(self)(self.name, fget, self.fset, self.fdel, self.__doc__, self.requirements)

    def setter(self, fset: Callable[[Any, Any], None]) -> "LazyProperty":
        return type(self)(self.name, self.fget, fset, self.fdel, self.__doc__, self.requirements)

    def deleter(self, fdel: Callable[[Any], None]) -> "LazyProperty":
        return type(self)(self.name, self.fget, self.fset, fdel, self.__doc__, self.requirements)


def lazyproperty(*requirements: Union[Requirable, str]) \
        -> Callable[[Callable[[Any], Any]], LazyProperty]:
    """Create a LazyProperty"""
    def lazydecorator(fget: Callable[[Any], Any]) -> LazyProperty:
        return LazyProperty(fget.__name__, fget, requirements=requirements)
    return lazydecorator

