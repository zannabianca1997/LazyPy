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
        self.eval_vars.require(call_on_every_invalidate=lambda sender, cause: self.invalidate(cause))


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

