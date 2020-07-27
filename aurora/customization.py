"""This is where the customization logic happens.
Let's have a runner instance for every device.
"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

from time import sleep
from duc_listener import DucListener
from helpers.logger import LoggerBuilder

log_builder = LoggerBuilder("mayo", __name__)
logger = log_builder.create_logger()


class CustomizationRunner:
    """Represents a Customization Runner"""

    def __init__(self, customize_to):
        self.customize_to = customize_to

    def __repr__(self):
        return f"{self.__class__.__name__}({self.customize_to})"

    def __str__(self):
        return f"A customization runner for {self.customize_to.upper()}"

    def start(self):
        print(f"Customizing: {self.customize_to}")


class CustomizationListener(DucListener):
    """Represents a Customization listener"""

    def __init__(self):
        logger.debug("Customization Listener Created...")
        self.started_cus_runners = []

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def add_duc(self, duc):
        logger.debug(f"Customizing: {duc}")

    def remove_duc(self, duc):
        logger.debug(f"Stopping: {duc}")


if __name__ == "__main__":
    cl = CustomizationListener()
    cr = CustomizationRunner("GLB")
