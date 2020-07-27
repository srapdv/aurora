"""An abstraction of the logging module"""
__author__ = "Jego Carlo Ramos"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

import logging
from logging.handlers import RotatingFileHandler
import yaml
import os
import sys
import pathlib


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


if __name__ == "__main__":
    logger_builder = LoggerBuilder("mayo", __name__)
    my_logger = logger_builder.create_logger()
    my_logger.info("Sample Log")
