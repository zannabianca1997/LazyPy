from typing import Any, Iterable, Callable, Optional

from .Validate import Invalidable, Validable, Cause
from .ValidateTypes import InvalidableMethod


class Requirable(Invalidable):
    """A object that can be required. When changed it will invalidate all requirer that required it"""
    __slots__ = []

    def _require(self) -> bool:
        """Require this object"""
        return True

    def require(self, call_on_next_invalidate: Optional[Callable[["Requirable", Any], None]] = None,
                call_on_every_invalidate: Optional[Callable[["Requirable", Any], None]] = None) -> bool:
        """Require this object. When the object change next the callback will be called"""
        if not self._require():
            return False
        if call_on_next_invalidate is not None:
            self.next_invalidate += lambda sender, cause: call_on_next_invalidate(self, cause)
        if call_on_every_invalidate is not None:
            self.has_invalidated += lambda sender, cause: call_on_every_invalidate(self, cause)
        return True


class Requirer(Validable, Requirable):
    """A object that needs other objects. Can be required too, will change when invalidated"""
    __slots__ = ["_requirements"]

    def __init__(self, requirements: Optional[Iterable[Requirable]] = ()):
        super().__init__()
        self._requirements = list(requirements)

    @property
    def requirements(self):
        return self._requirements

    @requirements.setter
    def requirements(self, requirements: Iterable[Requirable]):
        self._requirements = list(requirements)
        self.invalidate(self.ChangedRequirementList())

    class ChangedRequirement(Cause):
        __slots__ = ["requirement", "cause"]
        requirement: Requirable
        cause: Cause

        def __init__(self, requirement: Requirable, cause: Cause):
            self.requirement = requirement
            self.cause = cause

        def __str__(self):
            return f"Changed requirements {self.requirement}, cause: {self.cause}"

        def __repr__(self):
            return f"{type(self)}(requirement={self.requirement}, cause={self.cause})"

    class ChangedRequirementList(Cause):
        __slots__ = []

        def __str__(self):
            return "Changed requirements list"

        def __repr__(self):
            return f"{type(self)}()"

    def requirement_changed(self, requirement: "Requirable", cause: Cause) -> None:
        self.invalidate(self.ChangedRequirement(requirement, cause))  # it isn't valid anymore

    def _validate(self) -> bool:
        """Try to to require all the requirements. Some of them can be specified at runtime"""
        for requirement in self.requirements:
            hook = InvalidableMethod(self.requirement_changed)  # the callback
            # when this object will be invalidated next all hooks are invalidated too
            self.next_invalidate += lambda sender, cause: hook.invalidate(cause)
            if not requirement.require(call_on_next_invalidate=hook):
                return False
        # siamo riusciti a richiederli tutti...
        return super(Requirer, self)._validate()

    def _require(self) -> bool:
        """Try to validate before require itself"""
        if self.validate():  # try to validate
            return super()._require()
        return False  # failed to validate

    def require(self, call_on_next_invalidate: Optional[Callable[["Requirable", Any], None]] = None,
                call_on_every_invalidate: Optional[Callable[["Requirable", Any], None]] = None,
                call_on_every_validate: Optional[Callable[["Requirable", Any], None]] = None) -> bool:
        if not super().require(call_on_next_invalidate=call_on_next_invalidate,
                               call_on_every_invalidate=call_on_every_invalidate):
            return False
        if call_on_every_validate is not None:
            self.has_validated += lambda sender, cause: call_on_every_validate(self, cause)
        return True

