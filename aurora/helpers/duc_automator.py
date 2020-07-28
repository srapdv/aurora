"""A set of abstractions of the uiautomator2 module
Classes:
    DucAutomator
Function:
    safe_run

Misc Variables:
    __author__
    __copyright__
    __maintainer__
    logger_builder
    logger
"""
__author__ = "Jego Carlo Ramos, Simoun De Vera"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

from uiautomator2 import Device
from collections import namedtuple

from helpers.logger import LoggerBuilder, logger_decorator as ld
from helpers.common_decorators import safe_run

logger_builder = LoggerBuilder("stonehenge", __name__)
logger = logger_builder.create_logger()


class DucAutomator:
    def __init__(self, duc, customize_to):
        """Initializes the DucAutomator
        Parameters:
            duc (Duc) - The DUC data object (namedtuple) to automate
        """
        self.serial_no = duc.serial_no
        self.imei = duc.imei
        self.android_ver = duc.android_ver
        self.model_name = duc.model_name
        self.customize_to = customize_to
        self._duc = Device(self.serial_no)

        # Screen-size helpers
        self.y_display = self._duc.info["displayHeight"]
        self.x_display = self._duc.info["displayWidth"]
        self.y_mid = self.y_display / 2
        self.x_mid = self.x_display / 2

    def __repr__(self):
        return f"{self.__class__.__name__}(duc)"

    @ld(logger)
    @safe_run(logger)
    def turn_on_screen(self):
        """Turns the screen on"""
        self._duc.screen_on()

    @ld(logger)
    @safe_run(logger)
    def turn_off_screen(self):
        """Turns the screen off"""
        self._duc.screen_off()

    @ld(logger)
    @safe_run(logger)
    def press_home(self):
        """Press the Home button"""
        self._duc.press("home")

    @ld(logger)
    @safe_run(logger)
    def tap_by_text(self, keyword, match_type="contains"):
        """Taps an element on screen using text

        Parameters:
            keyword (str): The keyword to search for
            match_type (str): Check if the an element contains or exactly matches the keyword
        """
        # Check arguments
        match_type = str(match_type).lower()
        valid_match_types = ["contains", "exact"]
        if match_type not in valid_match_types:
            raise ValueError(
                f"The match_type value of {match_type} is not in {valid_match_types}"
            )
        else:
            if match_type == "contains":
                self._duc(textContains=keyword).click()
            else:
                self._duc(text=keyword).click()

    @ld(logger)
    @safe_run(logger)
    def scroll_to_text(self, keyword, match_type="contains"):
        """Scroll until an element on the screen is visible

        Parameters:
            keyword (str): The keyword to search for
            match_type (str): Check if the an element contains or exactly matches the keyword
        """
        # Check arguments
        match_type = str(match_type).lower()
        valid_match_types = ["contains", "exact"]
        if match_type not in valid_match_types:
            raise ValueError(
                f"The match_type value of {match_type} is not in {valid_match_types}"
            )
        self._duc(scrollable=True).scroll.to(text="keyword")

    @ld(logger)
    @safe_run(logger)
    def open_preconfig_screen(self):
        """Opens up the customization screen
        Returns:
            exit_code (int) - Returns 0 if successful, some other integer otherwise
        """
        dial_input = f"*%23272*{self.imei}"
        command = f"am start -a android.intent.action.DIAL -d tel:{dial_input}"

        exit_code = self._duc.shell(command).exit_code

        return exit_code


if __name__ == "__main__":
    Duc = namedtuple("Duc", "serial_no imei android_ver model_name")
    sample_duc = Duc("23c44de9ec1e7ece", "4545454", "9", "model")
    duc1 = DucAutomator(sample_duc)
    duc1.scroll_to_text("About phone", match_type="contains")
    duc1.tap_by_text("About phone", match_type="contains")
