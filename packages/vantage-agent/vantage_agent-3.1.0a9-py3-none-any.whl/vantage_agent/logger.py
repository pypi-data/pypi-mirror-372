"""Core module for logging operations."""

import functools
from traceback import format_tb

from buzz import DoExceptParams
from loguru import logger


def log_error(params: DoExceptParams):
    """Log a Buzz-based exception and the stack-trace of the error's context.

    :param: params: A DoExceptParams instance containing the original exception, a
                    message describing it, and the stack trace of the error.
    """
    logger.error(
        "\n".join(
            [
                params.final_message,
                "--------",
                "Traceback:",
                "".join(format_tb(params.trace)),
            ]
        )
    )


def logger_wraps(*, entry: bool = True, exit: bool = True, level: str = "DEBUG"):
    """Wrap a function with logging statements.

    Reference:
        https://loguru.readthedocs.io/en/stable/resources/recipes.html
    """

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        return wrapped

    return wrapper
