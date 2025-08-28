try:
    from .core_cython import BoolHybridArray
except ImportError:
    from .core import BoolHybridArray
__version__ = "7.10.8"
__all__ = ["BoolHybridArray", "__version__"]