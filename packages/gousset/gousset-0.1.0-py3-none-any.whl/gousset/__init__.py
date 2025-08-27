"""
Gousset - Your pocket profiler

Elegant, friendly timing for Python functions. Just instrument your modules
and get comprehensive timing statistics at program exit.

Example:
    import gousset
    import my_module

    gousset.instrument(my_module)
    # Use your functions normally - timing happens automatically
"""

from .core import instrument

__version__ = "0.1.0"
__author__ = "Your Name"
__all__ = ["instrument"]
