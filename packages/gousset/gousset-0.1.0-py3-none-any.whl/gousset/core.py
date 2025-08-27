"""
Core functionality for gousset timing profiler.
"""

import time
import atexit
import statistics
from functools import wraps
from collections import defaultdict
from typing import Any, Callable, Dict, List
import types
import inspect

# Module-level variables
_timings: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
_instrumented_modules = set()
_original_functions = {}  # Store original functions for potential restoration
_registered_exit = False


def _register_exit_handler() -> None:
    """Register exit handler only once"""
    global _registered_exit
    if not _registered_exit:
        atexit.register(_print_all_statistics)
        _registered_exit = True


def _print_all_statistics() -> None:
    """Print timing statistics for all instrumented modules"""
    if not _timings:
        return

    for module_name, functions in _timings.items():
        if not functions:
            continue

        print(f"\n=== Gousset Timing Statistics for Module: {module_name} ===")
        print("-" * 70)

        for func_name, times in functions.items():
            if not times:
                continue

            total_time = sum(times)
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0.0
            min_time = min(times)
            max_time = max(times)
            count = len(times)

            print(f"Function: {func_name}")
            print(f"  Calls:   {count:>8}")
            print(f"  Sum:     {total_time:>8.6f}s")
            print(f"  Average: {avg_time:>8.6f}s")
            print(f"  Std Dev: {std_time:>8.6f}s")
            print(f"  Min:     {min_time:>8.6f}s")
            print(f"  Max:     {max_time:>8.6f}s")
            print()


def _create_timed_function(
    original_func: Callable, func_name: str, module_name: str
) -> Callable:
    """Create a timed version of a function"""

    @wraps(original_func)
    def timed_wrapper(*args: Any, **kwargs: Any) -> Any:
        ts = time.time()
        result = original_func(*args, **kwargs)
        te = time.time()
        dt = te - ts

        # Store timing
        _timings[module_name][func_name].append(dt)
        return result

    return timed_wrapper


def instrument(module: Any) -> None:
    """
    Instrument all functions in a module to be timed automatically

    Args:
        module: The Python module to instrument. All functions in the module
               will be wrapped to collect timing statistics.

    Example:
        import gousset
        import my_module

        gousset.instrument(my_module)
        # All functions in my_module are now timed automatically
    """
    _register_exit_handler()

    module_name = getattr(module, "__name__", "unknown_module")

    if module_name in _instrumented_modules:
        return  # Already instrumented

    _instrumented_modules.add(module_name)

    # Get all functions in the module and instrument them
    for name in dir(module):
        obj = getattr(module, name)
        # Check for any callable that's not a class and not private
        if (
            callable(obj)
            and not name.startswith("_")
            and not inspect.isclass(obj)
            and not inspect.ismodule(obj)
        ):
            # Store original for potential restoration
            _original_functions[f"{module_name}.{name}"] = obj

            # Create timed version
            timed_func = _create_timed_function(obj, name, module_name)

            # Replace in module
            setattr(module, name, timed_func)
