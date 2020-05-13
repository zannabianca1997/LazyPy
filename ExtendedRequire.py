from collections import deque, abc
from itertools import chain
from typing import Optional, Iterable, Union, Dict, Any, Tuple, Callable

from .RequireTypes import RequirableDict
from .Require import Requirer, Requirable


class StrRequirer(Requirer):
    """A requirer that can accept string require"""
    __slots__ = ["_str_requirements", "eval_vars"]

    def __init__(self, requirements: Optional[Iterable[Union[Requirable, str]]] = (),
                 eval_vars: Optional[Dict[str, Any]] = None):
        """Requirements can be str or Requirable. string ones will be evaluated at runtime"""
        abs_requirements, self._str_requirements = self._divide_requirements(requirements)
        super().__init__(*abs_requirements)
        self.eval_vars = RequirableDict(eval_vars)
        # when the vars change this will be invalidated
        self.eval_vars.permanent_require(call_on_every_invalidate=lambda sender, cause: self.invalidate(cause))


    def _divide_requirements(self, requirements: Iterable[Union[Requirable, str]]) \
            -> Tuple[Iterable[Requirable], Iterable[str]]:
        """Divide the various type of requirements the class can accept"""
        str_requirements = deque()
        abs_requirements = deque()
        for req in requirements:
            if isinstance(req, str):
                str_requirements.append(req)
            else:
                abs_requirements.append(req)
        return abs_requirements, str_requirements



    @Requirer.requirements.getter
    def requirements(self):
        # we need to iterprete the str requirements
        rel_requirements = deque()
        for obj in (eval(obj, {}, self.eval_vars) for obj in self._str_requirements):
            if isinstance(obj, Requirable):
                rel_requirements.append(obj)
                continue
            # then maybe is an iterable?
            if isinstance(obj, abc.Iterable):
                rel_requirements.extend(obj)
                continue
            # last chance, a Nonetype (for ifs)
            if obj is None:
                continue
            raise TypeError(
                f"String requirement should evaluate to Requirable or Iterable of Requirables, got {type(obj)}"
            )

        return list(chain(
            Requirer.requirements.fget(self),
            rel_requirements
        ))

    @requirements.setter
    def requirements(self, requirements: Union[Requirable, str]):
        # we need to separate the str ones
        abs_requirements, self._str_requirements = self._divide_requirements(requirements)
        Requirer.requirements.fset(self, abs_requirements)


if __name__ == "__main__":
    class NamedRequirable(Requirable):
        def __init__(self, name):
            super().__init__()
            self.__name__ = name

        def __str__(self):
            return self.__name__

        def require(self, call_on_next_invalidate: Callable[["Requirable", Any, Any], None]) -> bool:
            print(f"Requiring {self.__name__}")
            return super().require(call_on_next_invalidate)

    class NamedRequirer(Requirer):
        def __init__(self, name, requirements=()):
            super().__init__(requirements)
            self.__name__ = name

        def __str__(self):
            return self.__name__

        def require(self, call_on_next_invalidate: Callable[["Requirable", Any, Any], None]) -> bool:
            print(f"Requiring {self.__name__}")
            return super().require(call_on_next_invalidate)

    class NamedStrRequirer(StrRequirer):
        def __init__(self, name, requirements=()):
            super().__init__(requirements)
            self.__name__ = name

        def __str__(self):
            return self.__name__

        def require(self, call_on_next_invalidate: Callable[["Requirable", Any, Any], None]) -> bool:
            print(f"Requiring {self.__name__}")
            return super().require(call_on_next_invalidate)

    A = NamedRequirable("A")
    B = NamedRequirable("B")
    C = NamedRequirable("C")

    D = NamedStrRequirer("D")
    E = NamedRequirer("E")

    F = NamedRequirer("F")

    for requirer in (D, E, F):
        requirer.has_validated += lambda sender: print(f"{sender} has validated")
        requirer.has_invalidated += lambda sender, cause: print(f"{sender} has invalidated cause: {cause}")

    E.requirements = A, B
    D.requirements = A, "omega"

    F.requirements = E,

    print("Validating F. Should request A, B and validate E and F")
    F.validate()
    print("Validating D. Should request A, E. This should not validate anything else")
    D.eval_vars["omega"] = E
    D.validate()
    print("Changing eval vars of D. This should invalidate D")
    D.eval_vars["omega"] = F
    print("Validating D, then invalidating E. This should invalidate F and D too")
    D.validate()
    E.invalidate("Test invalidate")
