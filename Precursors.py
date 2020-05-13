import functools
from typing import Any, Type


class Precursor:
    """Maintains an instance attribute on every object"""
    __slots__ = ["__name__"]
    CREATE_BEFORE_INIT = 0
    CREATE_AFTER_INIT = 1
    create_when = CREATE_BEFORE_INIT

    def get_instance_attribute(self, obj: Any) -> Any:
        """Initialize the instance attribute object"""
        raise NotImplemented()

    def create_in(self, obj: Any) -> None:
        """Create the instance attribute"""
        obj.__dict__[self.__name__] = self.get_instance_attribute(obj)

    def delete_in(self, obj: Any) -> None:
        """delete the instance attribute"""
        del obj.__dict__[self.__name__]

    def is_in(self, obj: Any) -> bool:
        """check if the instance attribute has been created"""
        return self.__name__ in obj.__dict__


def has_precursors(cls: type) -> type:
    """Decorate a class that has cached attributes"""
    # first we find all objects that need cache
    need_initialization = [
        (name, obj) for name, obj in ((attr, getattr(cls, attr)) for attr in cls.__dict__)
        if isinstance(obj, Precursor)
    ]
    if need_initialization:
        for name, obj in need_initialization:
            obj.__name__ = name  # setting names
        create_before_init = [obj for _, obj in need_initialization if obj.create_when == obj.CREATE_BEFORE_INIT]
        create_after_init = [obj for _, obj in need_initialization if obj.create_when == obj.CREATE_AFTER_INIT]
        old_init = cls.__init__

        # we define a new __init__ method
        @functools.wraps(old_init)
        def __init__(self, *args, **kwargs):
            for obj in create_before_init:
                obj.create_in(self)
            old_init(self, *args, **kwargs)
            for obj in create_after_init:
                obj.create_in(self)

        cls.__init__ = __init__
    return cls


if __name__=="__main__":
    class Hello(Precursor):
        def get_instance_attribute(self, obj: Any) -> Any:
            return "Hello World"

    @has_precursors
    class Foo:
        attrib = Hello()

    bar = Foo()
    print(bar.attrib)
    print(type(bar).attrib)