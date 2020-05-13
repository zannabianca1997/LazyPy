from .Events import Event, CleaningEvent

class Cause:
    __slots__ = []
    pass

class Invalidable:
    """A object that will signal when it's invalidated"""
    __slots__ = ["has_invalidated", "next_invalidate"]

    def __init__(self):
        self.has_invalidated = Event()
        self.next_invalidate = CleaningEvent()
        self.has_invalidated += self.next_invalidate  # when it invalidate, call (and clear) next_invalidate

    def invalidate(self, cause: Cause):
        """Invalidate the object"""
        self.has_invalidated(self, cause)


class Validable(Invalidable):
    """An object that can be asked to be valid"""
    __slots__ = ["_valid", "has_validated"]

    def __init__(self):
        super().__init__()
        self._valid = False
        self.has_validated = Event()

    def _validate(self) -> bool:
        """try to validate the object. return if it managed to"""
        self._valid = True
        self.has_validated(self)
        return True

    def validate(self) -> bool:
        """try to validate only if it isn't valid"""
        if not self.valid:
            return self._validate()
        return True

    def _invalidate(self, cause: Cause) -> None:
        self._valid = False
        super().invalidate(cause)

    def invalidate(self, cause: Cause) -> None:
        """Invalidate the object only if it is valid"""
        if self.valid:
            self._invalidate(cause)

    @property
    def valid(self):
        return self._valid
