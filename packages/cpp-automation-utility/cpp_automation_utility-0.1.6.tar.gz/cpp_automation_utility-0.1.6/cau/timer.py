"""Timer module."""
import functools
import logging
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("CAU")

def timer(func: Callable) -> Callable:
    """
    Timer function to time a command.

    Args:
        func (Callable): function to time

    Returns:
        Callable: wrapper function
    """

    @functools.wraps(func)
    def timer_wrapper(*args, **kwargs) -> Any: # noqa: ANN002, ANN003, ANN401
        """
        Wraps function.

        Returns:
            _type_: function result
        """
        start = time.perf_counter_ns()
        logger.debug("Entering %s", func.__name__)
        try:
            result = func(*args, **kwargs)
        finally:
            logger.info("%s completed in %d ms", func.__name__, (time.perf_counter_ns() - start)/1.0e6)
        return result

    return timer_wrapper
