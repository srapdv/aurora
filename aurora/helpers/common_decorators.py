"""Collection of custom-made function decorators"""
__author__ = "Jego Carlo Ramos"
__maintainer__ = "Jego Carlo Ramos"
__note__ = "Please do not modify"

from functools import wraps
import logging
import time

# Decorators built from Classes are also a thing, but they come
# with some limitations with the help() function
# Reference:
# https://stackoverflow.com/questions/25973376/functools-update-wrapper-doesnt-work-properly/25973438#25973438


def safe_run(logger_instance=None):
    """Handles and logs (if a logging.LoggerAdapter is passed) all exceptions of the original function

    Parameters:
        logger_instance (logging.LoggerAdapter) - The logger instance from the logging module (optional)
    """

    def inner_func(orig_function):
        @wraps(orig_function)
        def wrapper(*args, **kwargs):
            try:
                result = orig_function(*args, **kwargs)
                return result
            except Exception as e:
                # Type check
                if isinstance(logger_instance, logging.LoggerAdapter):
                    logger_instance.error(
                        f"{orig_function.__name__} threw an Error: {e}"
                    )
                return None

        return wrapper

    return inner_func


def singleton(orig_class):
    """Transforms the class to a singleton
    Notes:
        Remember to keep your class thread-safe
    """
    # TODO: Implementation
    pass
