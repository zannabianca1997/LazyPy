from abc import abstractmethod
from collections import abc
from typing import Optional, Any, Iterator, overload, Iterable, KeysView, ValuesView, ItemsView, \
    MutableSequence, MutableMapping, Union

from .Require import Requirable
from .Validate import Cause


class RequirableDict(abc.MutableMapping, Requirable):
    """A dict that will invalidate when it's changed"""
    __slots__ = ["_dict"]
    def __init__(self, _dict:Optional[MutableMapping[Any, Any]] = None):
        super().__init__()
        self._dict = _dict if _dict is not None else {}

    class KeyChanged(Cause):
        __slots__ = ["key"]
        def __init__(self, key):
            self.key = key
        def __str__(self):
            return f"Key {self.key} has changed"

    class KeyDeleted(KeyChanged):
        def __str__(self):
            return f"Key {self.key} has been deleted"

    def __setitem__(self, k: Any, v: Any) -> None:
        self._dict.__setitem__(k, v)
        self.invalidate(self.KeyChanged(k))

    def __delitem__(self, k: Any) -> None:
        self._dict.__delitem__(k)
        self.invalidate(self.KeyDeleted(k))

    def __getitem__(self, k: Any) -> Any:
        return self._dict.__getitem__(k)

    def __len__(self) -> int:
        return self._dict.__len__()

    def __iter__(self) -> Iterator[Any]:
        return self._dict.__iter__()

    def __str__(self) -> str:
        return self._dict.__str__()

    def __repr__(self) -> str:
        return f"{type(self)}({self._dict.__str__()})"


class RequirableList(abc.MutableSequence,Requirable):
    __slots__ = ["_list"]

    def __init__(self, _list:Optional[Iterable[Any]] = ()):
        super().__init__()
        self._list = list(_list)

    class ChangedElement(Cause):
        __slots__ = ["element"]
        def __init__(self, element: Any):
            self.element = element
        def __str__(self):
            return f"{self.element} was changed in the list"

    class InsertedElement(ChangedElement):
        __slots__ = ["element"]
        def __init__(self, element: Any):
            self.element = element
        def __str__(self):
            return f"{self.element} was inserted in the list"

    class DeletedElement(ChangedElement):
        __slots__ = ["element"]
        def __init__(self, element: Any):
            self.element = element
        def __str__(self):
            return f"{self.element} was popped from the list"

    def insert(self, index: int, obj: Any) -> None:
        self._list.insert(index, obj)
        self.invalidate(self.InsertedElement(obj))

    def __getitem__(self, i: Union[int, slice]) -> Union[Any, "RequirableList"]:
        res = self._list.__getitem__(i)
        if isinstance(i, int):
            return res
        res = RequirableList(res)
        res.has_invalidated += self.has_invalidated  # so every change in the slice is signalled back
        return res

    def __setitem__(self, i: Union[int, slice], o: Union[Any, Iterable[any]]) -> None:
        self._list.__setitem__(i,o)
        self.invalidate(self.ChangedElement(i))

    def __delitem__(self, i: Union[int, slice]) -> None:
        self._list.__delitem__(i)
        self.invalidate(self.DeletedElement(i))

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self):
        yield from self._list

    def __str__(self):
        return f"{type(self).__name__}({self._list})"

class RequirableMethod(Requirable):
    """Every time is called this method will invalidate"""
    __slots__ = ["name"]

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    class MethodCalled(Cause):
        __slots__ = ["method_name"]

        def __init__(self, name: str):
            self.method_name = name

        def __str__(self):
            return f"Method {self.method_name} was called"

    def __call__(self):
        self.invalidate(self.MethodCalled(self.name))