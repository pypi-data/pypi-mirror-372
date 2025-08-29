"""Utils for regex functions."""

from collections.abc import Callable
from functools import wraps


def enforce_str_arg(func: Callable) -> Callable:
    """Enforce input arg to func is string.

    Args:
        func (Callable): function to decorate

    Raises:
        TypeError: If the input arg `text` is not a string.
    """

    @wraps(func)
    def wrapper(text: str) -> bool:
        if not isinstance(text, str):
            msg = (
                "Argument 'text' must be of type str, "
                f'got {type(text).__name__}'
            )
            raise TypeError(msg)
        return func(text)

    return wrapper
