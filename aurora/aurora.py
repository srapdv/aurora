"""Entry point of the application"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

from customization import CustomizationRunner, CustomizationListener
from duc_monitor import DucMonitor, DucAuthFilter
from signal_handler import SignalHandler
from helpers.logger import LoggerBuilder

log_builder = LoggerBuilder("mayo", __name__)
logger = log_builder.create_logger()

logger.info("App Starting...")

cl = CustomizationListener()

dm = DucMonitor(cl)
dm.start()

# The main thread will pause until a SIGINT (Ctrl + C) is intercepted
SignalHandler.listen_for_sigint()
