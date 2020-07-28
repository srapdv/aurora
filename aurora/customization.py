"""This is where the customization logic happens.
Let's have a runner instance for every device.
"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

from time import sleep
from duc_listener import DucListener
from helpers.logger import LoggerBuilder
from helpers.duc_automator import DucAutomator


log_builder = LoggerBuilder("stonehenge", __name__)
logger = log_builder.create_logger()


class CustomizationRunner:
    """Represents a Customization Runner"""

    def __init__(self, duc, customize_to):
        self.duc_automator = DucAutomator(duc, customize_to)
        self.customize_to = customize_to
        self.running_threads = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self.customize_to})"

    def __str__(self):
        return f"A customization runner for {self.customize_to.upper()}"

    def start(self):
        da = self.duc_automator
        logger.info(f"Customizing: {da.imei} to {self.customize_to}")
        self.running_threads.append(da)

        da.turn_on_screen()
        da.open_preconfig_screen()
        da.tap_by_text("#", match_type="exact")


class CustomizationListener(DucListener):
    """Represents a Customization listener"""

    def __init__(self):
        logger.debug("Customization Listener Created...")
        self.started_cus_runners = []

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def add_duc(self, duc):
        # TODO: Where will the customize_to come from?
        cus_runner = CustomizationRunner(duc, "glb")
        logger.debug(f"Customizing: {duc}")
        cus_runner.start()

    def remove_duc(self, duc):
        logger.debug(f"Stopping: {duc}")


if __name__ == "__main__":
    cl = CustomizationListener()
    cr = CustomizationRunner("GLB")
