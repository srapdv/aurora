"""An abstraction and a decorator for the logging module"""
__author__ = "Jego Carlo Ramos"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import yaml
import os
import sys
import pathlib
import time


class LoggerBuilder:
    """Represents a Logger Builder"""

    _config = None

    def __init__(self, code_name, module_name=__name__):
        """Initializes and configures the builder"""
        self._module_name = module_name

        # We'll make this a dictionary to have it as a setable attr
        # to a logging instance
        self._code_name = {"code_name": code_name}
        # Enforce _codename value
        if not self._code_name:
            raise ValueError("No code_name was set!")

        LoggerBuilder._configure_and_resolve_paths()

    @classmethod
    def _configure_and_resolve_paths(cls):
        """Adds logging configs and resolve paths"""

        # Load values from the logging_config.yaml
        base_path = pathlib.Path(__file__).absolute()
        config_path = f"{base_path.parents[1]}/config/logging_config.yaml"

        with open(config_path, "r",) as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

        cls._log_file_path = config["logger"]["handlers"]["file"]["filename"]
        cls._log_format = config["logger"]["format"]
        cls._log_level_str = config["logger"]["level"]
        cls._console_level = config["logger"]["handlers"]["console"]["level"]
        cls._file_level = config["logger"]["handlers"]["file"]["level"]
        cls._file_max_size = config["logger"]["handlers"]["file"]["max_bytes"]
        cls._file_backup_count = config["logger"]["handlers"]["file"]["backup_count"]

    def create_logger(self):
        """Creates and returns a logger instance"""

        # Set-up the logging module
        logger = logging.getLogger(self._module_name)
        debug_level = getattr(logging, LoggerBuilder._log_level_str)
        logger.setLevel(debug_level)
        formatter = logging.Formatter(LoggerBuilder._log_format)

        # Add file handler
        file_handler = RotatingFileHandler(
            LoggerBuilder._log_file_path,
            maxBytes=LoggerBuilder._file_max_size,
            backupCount=LoggerBuilder._file_backup_count,
        )
        file_handler.setFormatter(formatter)
        file_log_level = getattr(logging, LoggerBuilder._file_level)
        file_handler.setLevel(file_log_level)

        # Add stream handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        console_log_level = getattr(logging, LoggerBuilder._console_level)
        file_handler.setLevel(console_log_level)

        # Add all handlers
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        # Inject code_name
        logger.codename = self._code_name

        return logging.LoggerAdapter(logger, self._code_name)


# Decorators built from Classes are also a thing, but they come
# with some limitations with the help() function
# Reference:
# https://stackoverflow.com/questions/25973376/functools-update-wrapper-doesnt-work-properly/25973438#25973438
def logger_decorator(logger_instance, log_level="debug"):
    """A function decorator that logs the execution time and signature
    of the original function

    Parameters:
        logger_instance (logging.LoggerAdapter) - A logger instance from the logging module
        log_level (str) - The logging debug level
    Returns:
        wrapped_function (function) - The decorated original function
    Raises:
        ValueError - If the logger_instance is not an instance of logging.LoggerAdapter
        ValueError - If the log_level is not in ["info", "debug", "warning", "error", "critical"]
    """

    log_level_clean = str(log_level).lower()

    # Type check
    if not isinstance(logger_instance, logging.LoggerAdapter):
        raise ValueError(
            "The logger instance passed is not a child of logging.LoggerAdapter"
        )

    # Invalid value check
    valid_levels = ["info", "debug", "warning", "error", "critical"]
    if log_level_clean not in valid_levels:
        raise ValueError(
            f"Invalid log level passed: {log_level}, valid values: {valid_levels}"
        )

    def inner_func(original_func):
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            # Capture the execution time
            t1 = time.time()
            result = original_func(*args, **kwargs)
            t2 = time.time()
            t = str(round(t2 - t1, 2))

            # Log the signature and execution time
            msg = f"Ran {original_func.__name__}() for {t} secs with args: {args} and kwargs: {kwargs}"
            log = getattr(logger_instance, log_level_clean)
            log(msg)
            return result

        return wrapper

    return inner_func


if __name__ == "__main__":
    logger_builder = LoggerBuilder("mayo", __name__)
    my_logger = logger_builder.create_logger()
    my_logger.info("Sample Log")

    @logger_decorator(my_logger, "warning")
    def sample_func(name):
        print(name)

    sample_func("hello")
