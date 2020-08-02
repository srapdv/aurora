"""This is where the customization logic happens.
Let's have a runner instance for every device.
Misc Variables:
    __author__
    __copyright__
    __maintainer__
"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Simoun De Vera"

import adbutils
import uiautomator2 as u2
import pathlib
import threading
from time import sleep
from threading import Thread

from helpers.interface_listeners import DucListener
from helpers.logger import LoggerBuilder, logger_decorator as ld
from helpers.duc_automator import DucAutomator
from operation_results import ReportsListener
from config_resolver import CustomizationConfigLoader as ccl


log_builder = LoggerBuilder("stonehenge", __name__)
logger = log_builder.create_logger()


class CustomizationRunner(Thread):
    """Represents a Customization Runner"""

    def __init__(self, duc, customize_to, *listeners):
        """Initializes the CustomizationRunner
        Parameters:
            duc (Duc) - The DUC data object (namedtuple) to automate
            customize_to - Where the DUC should be customized to
            listeners (*args of CustomizationListeners) - arbitrary number of listeners
        """
        self.duc = duc
        self.customize_to = customize_to.upper()

        # Check if listeners implemented the required interface
        self.listeners = []
        for listener in listeners:
            if not isinstance(listener, ReportsListener):
                msg = f"Ignored {str(listener)} because it is not a child of {ReportsListener.__name__}"
                logger.error(msg)
            else:
                self.listeners.append(listener)

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
            self._start_customization_process()
            for listener in self.listeners:
                listener.passed(self.duc, self.customize_to)
        except (AssertionError, adbutils.AdbError, u2.UiObjectNotFoundError) as e:
            logger.error(f"Expected Error: {e}")
            for listener in self.listeners:
                listener.failed(self.duc, self.customize_to)
        except Exception as e:
            logger.critical(f"Unexpected Error: {e}")
            for listener in self.listeners:
                listener.failed(self.duc, self.customize_to)

    @ld(logger)
    def _start_customization_process(self):
        self.duc_automator = DucAutomator(self.duc, self.customize_to)
        da = self.duc_automator
        logger.info(f"Customizing: {da.imei} to {self.customize_to}")

        # Recover when the screen is turned off
        da.unlock_screen()

        da.dial(f"*%23272*{da.imei}")
        da.tap_by_text("#", match_type="exact")

        sleep(1)  # For the android 8.1 (Lite)

        da.scroll_to_text(self.customize_to)
        sleep(1.5)  # For some DUCs, the scroll animation needs some time to settle
        da.tap_by_text(self.customize_to)

        da.tap_by_text("INSTALL")
        da.confirm_install()


class CustomizationListener(DucListener):
    """Represents a Customization listener"""

    def __init__(self):
        logger.debug("Customization Listener Created...")
        self.active_runners = []

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def add_duc(self, duc):
        customize_to = ccl.load_customize_to()
        rl = ReportsListener()
        cus_runner = CustomizationRunner(duc, customize_to, rl)
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
