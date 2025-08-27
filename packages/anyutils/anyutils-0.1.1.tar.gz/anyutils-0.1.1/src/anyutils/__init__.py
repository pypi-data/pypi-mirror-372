# Expose the most useful utilities at the top level of the package.
from .decorators.timer import timeit


# You can also define a __all__ to control what `from pyutils import *` imports
__all__ = [
    'timeit',
]