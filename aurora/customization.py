"""This is where the customization logic happens.
Let's have a runner instance for every device.
"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

import adbutils
import uiautomator2 as u2
import concurrent.futures
import threading
from time import sleep
from threading import Thread

from duc_listener import DucListener
from helpers.logger import LoggerBuilder, logger_decorator as ld
from helpers.duc_automator import DucAutomator


log_builder = LoggerBuilder("stonehenge", __name__)
logger = log_builder.create_logger()


class CustomizationRunner(Thread):
    """Represents a Customization Runner"""

    def __init__(self, duc, customize_to):
        """Initializes the CustomizationRunner
        Parameters:
            duc (Duc) - The DUC data object (namedtuple) to automate
            customize_to - Where the DUC should be customized to
        """
        self.duc = duc
        self.customize_to = customize_to.upper()

        # Call the __init__() of the Thread class
        super().__init__()
        # Kill this thread if the Main thread stops
        self.daemon = True

    def __repr__(self):
        return f"{self.__class__.__name__}({self.customize_to})"

    def __str__(self):
        return f"A customization runner for {self.customize_to}"

    @ld(logger)
    def run(self):
        try:
            self.duc_automator = DucAutomator(self.duc, self.customize_to)
            da = self.duc_automator
            logger.info(f"Customizing: {da.imei} to {self.customize_to}")

            # Recover when the screen is turned off
            da.unlock_screen()
            sleep(2)  # Some DUCs have unlock animations

            da.dial(f"*%23272*{da.imei}")
            da.tap_by_text("#", match_type="exact")
            da.scroll_to_text(self.customize_to)
            sleep(1.5)  # For some DUCs, the scroll animation needs some time to settle
            da.tap_by_text(self.customize_to)

            da.tap_by_text("INSTALL")
            da.tap_by_text("Sales")
            # da.tap_by_text("OK")
            logger.info(f"PASSED:\t{self.duc_automator.imei} to {self.customize_to}")
        except (AssertionError, adbutils.AdbError, u2.UiObjectNotFoundError) as e:
            logger.info(f"FAILED:\t{self.duc_automator.imei} to {self.customize_to}")
            logger.debug(f"Expected Error: {e}")
        except Exception as e:
            logger.info(f"FAILED:\t{self.duc_automator.imei} to {self.customize_to}")
            logger.critical(f"Unexpected Error: {e}")


class CustomizationListener(DucListener):
    """Represents a Customization listener"""

    def __init__(self):
        logger.debug("Customization Listener Created...")
        self.active_runners = []

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def add_duc(self, duc):
        # TODO: Where will the customize_to come from?
        cus_runner = CustomizationRunner(duc, "glb")
        logger.debug(f"Customizing: {duc}")

        if duc not in self.active_runners:
            self.active_runners.append(duc)
            cus_runner.start()

        logger.debug(f"Active Runners: {self.active_runners}")
        logger.debug(f"Active thread count: {threading.active_count()}")

    def remove_duc(self, duc):
        logger.debug(f"Stopping: {duc}")

        try:
            # Ignore the KeyError
            self.active_runners.remove(duc)
        except ValueError:
            pass

        logger.debug(f"Active Runners: {self.active_runners}")
        logger.debug(f"Active thread count: {threading.active_count()}")


if __name__ == "__main__":
    cl = CustomizationListener()
    cr = CustomizationRunner("GLB")
