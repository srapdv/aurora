"""Entry point of the application"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"


from customization import CustomizationRunner
from dut_monitor import DutMonitor

adm = DutMonitor()
adm.start()
