"""Entry point of the application"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

import sys
import signal
from customization import CustomizationRunner
from dut_monitor import DutMonitor, DutAuthFilter

print("App Running...")

adm = DutMonitor()
adm.start()


def signal_handler(sig, frame):
    print(f"KeyboardInterrupt (ID: {sig}) has been caught. Exiting Application...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.pause()
