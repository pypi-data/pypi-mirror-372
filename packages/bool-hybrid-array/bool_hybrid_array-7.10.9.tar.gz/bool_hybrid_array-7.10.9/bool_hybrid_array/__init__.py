import sys
from types import ModuleType
try:
    from . import core_cython as core
except ImportError:
    from . import core
__version__ = "7.10.9"
public_objects = []
for name in dir(core):
    if not name.startswith("_"):
        obj = getattr(core, name)
        if isinstance(obj, (type, ModuleType)) or callable(obj):
            public_objects.append(name)
__all__ = public_objects + ["__version__"]
globals().update({
    name: getattr(core, name)
    for name in public_objects
})
