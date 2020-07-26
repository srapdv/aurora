"""Entry point of the application"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

from customization import CustomizationRunner
from duc_monitor import DucMonitor, DucAuthFilter
from signal_handler import SignalHandler

print("App Starting...")

dm = DucMonitor()
dm.start()

# The main thread will pause until a SIGINT (Ctrl + C) is intercepted
SignalHandler.listen_for_sigint()
