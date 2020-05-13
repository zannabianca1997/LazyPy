from .LazyProperties import lazyproperty
from .RequireTypes import RequirableMethod, RequirableDict, RequirableList

__doc__ = "Contains the methods to lazily evaluate properties of an object, with a dependencies system to reveal " \
          "when those properties are changed."