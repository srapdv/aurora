"""Handles and persists operations and customization data
Misc Variables:
    __author__
    __copyright__
    __maintainer__
    __log_builder__
    __logger__
"""
__author__ = "Jego Carlo Ramos"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

import csv
import pathlib
import datetime
import os

from helpers.interface_listeners import CustomizationListener
from helpers.logger import LoggerBuilder

logger_builder = LoggerBuilder("stonehenge", __name__)
logger = logger_builder.create_logger()


class ReportsListener(CustomizationListener):
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def started(self, duc, customized_to):
        logger.info(f"Started: {duc} -> {customized_to}")

    def passed(self, duc, customized_to):
        logger.info(f"Passed: {duc} -> {customized_to}")
        self._write_to_tsv(duc, "PASSED", customized_to)

    def failed(self, duc, customized_to):
        logger.info(f"Failed: {duc} -> {customized_to}")
        self._write_to_tsv(duc, "FAILED", customized_to)

    def skipped(self, duc, customized_to):
        logger.info(f"Skipped: {duc} -> {customized_to}")
        self._write_to_tsv(duc, "SKIPPED", customized_to)

    def completed(self, duc, customized_to):
        logger.info(f"Completed: {duc} -> {customized_to}")

    def _write_to_tsv(self, duc, status, customized_to):
        # Resolve tsv location
        base_path = pathlib.Path(__file__).absolute()
        results_path = f"{base_path.parents[1]}/aurora/out/reports"
        today = datetime.datetime.today()
        file_name = results_path + f"/{today.strftime('%d_%B_%Y')}.tsv"

        with open(file_name, "a+") as f:
            tsv_writer = csv.writer(f, delimiter="\t")
            # STATUS    IMEI    MODEL_NAME      CUSTOMIZED_TO   TIME_STAMP
            imei = duc.imei
            model_name = duc.model_name
            customized_to = customized_to
            timestamp = datetime.datetime.now()
            tsv_writer.writerow([status, imei, model_name, customized_to, timestamp])
