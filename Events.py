from collections import deque
from typing import Any


class Event:
    __slots__ = ["handlers"]
    """Represent a event"""
    def __init__(self):
        self.handlers = deque()

    def add(self, handler):
        """add a handler"""
        self.handlers.append(handler)
        return self

    def remove(self, handler):
        """remove the handler"""
        self.handlers.remove(handler)
        return self

    def fire(self, sender: Any, *args, **kwargs):
        """fire the event"""
        for handler in self.handlers:
            handler(sender, *args, **kwargs)

    def clear(self):
        """delete all handlers"""
        self.handlers = deque()

    __iadd__ = add
    __isub__ = remove
    __call__ = fire


class CleaningEvent(Event):
    """when this event is fired all the handlers are reset"""
    __slots__ = []

    def fire(self, sender: Any, *args, **kwargs):
        while self.handlers:
            self.handlers.pop()(sender, *args, **kwargs)