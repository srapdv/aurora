"""A set of abstractions of the uiautomator2 package and ADB shell commands
Classes:
    DucAutomator

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

import uiautomator2 as u2
from collections import namedtuple
from threading import Thread

from helpers.logger import LoggerBuilder, logger_decorator as ld

logger_builder = LoggerBuilder("stonehenge", __name__)
logger = logger_builder.create_logger()


class DucAutomator:
    def __init__(self, duc, customize_to):
        """Initializes the DucAutomator
        Parameters:
            duc (Duc) - The DUC data object (namedtuple) to automate
            customize_to - Where the DUC should be customized to
        """
        self.serial_no = duc.serial_no
        self.imei = duc.imei
        self.android_ver = duc.android_ver
        self.model_name = duc.model_name
        self.customize_to = customize_to
        self._duc = u2.Device(self.serial_no)

    def __repr__(self):
        return f"{self.__class__.__name__}(duc)"

    @ld(logger)
    def unlock_screen(self):
        """Unlocks the screen

        Raises:
            AssertionError - If the device unlock shell command did not work
        """

        # The unlock() method from uiautomator2 does not
        # work if the DUC is currently locked with the screen turned on
        if self._duc.info.get("screenOn"):
            exit_code = self._duc.shell("input keyevent 82").exit_code
            if exit_code != 0:
                raise AssertionError("Unable to unlock screen")

        self._duc.unlock()

    @ld(logger)
    def turn_on_screen(self):
        """Turns the screen on"""
        self._duc.screen_on()

    @ld(logger)
    def turn_off_screen(self):
        """Turns the screen off"""
        self._duc.screen_off()

    @ld(logger)
    def press_home(self):
        """Press the Home button"""
        self._duc.press("home")

    @ld(logger)
    def tap_by_text(self, keyword, match_type="contains"):
        """Taps an element on screen using text

        Parameters:
            keyword (str): The keyword to search for
            match_type (str): Valid types ["exact", "contains", "starts_with"]
        """
        selector = {
            "selector_type": "by_text",
            "selector_value": keyword,
            "selector_meta": match_type,
        }
        el = self._get_element(selector)

        el.click()

    @ld(logger)
    def scroll_to_text(self, keyword, match_type="starts_with"):
        """Scroll until an element on the screen is visible

        Parameters:
            keyword (str): The keyword to search for
            match_type (str): Valid types ["exact", "contains", "starts_with"]
        """

        # Check if there is a scrollable element in the screen
        found_scrollable = self._duc(scrollable=True)
        if not found_scrollable.exists(timeout=1):
            logger.debug("Pre-config screen not scrollable")
            return

        steps = 100
        max_swipes = 1_000
        if match_type == "exact":
            self._duc(scrollable=True).scroll.to(
                steps=steps, max_swipes=max_swipes, text=keyword
            )
        elif match_type == "contains":
            self._duc(scrollable=True).scroll.to(
                steps=steps, max_swipes=max_swipes, textContains=keyword
            )
        elif match_type == "starts_with":
            self._duc(scrollable=True).scroll.to(
                steps=steps, max_swipes=max_swipes, textStartsWith=keyword
            )

    @ld(logger)
    def dial(self, dial_input):
        """Opens the dialer and dials the input provided
        Returns:
            exit_code (int) - Returns 0 if successful, some other integer otherwise
        """

        command = f"am start -a android.intent.action.DIAL -d tel:{dial_input}"

        exit_code = self._duc.shell(command).exit_code

        return exit_code

    def _get_element(self, keypair):
        selector_type = keypair.get("selector_type")
        selector_value = keypair.get("selector_value")
        selector_meta = keypair.get("selector_meta")

        if selector_type == "by_text":

            # Check valid meta
            selector_meta = str(selector_meta).lower()
            valid_selector_meta = ["contains", "exact", "starts_with"]
            if selector_meta not in valid_selector_meta:
                raise ValueError(
                    f"The match_type value of {selector_meta} is not in {valid_selector_meta}"
                )

            el = None
            if selector_meta == "exact":
                el = self._duc(text=selector_value)
            elif selector_meta == "contains":
                el = self._duc(textContains=selector_value)
            elif selector_meta == "starts_with":
                el = self._duc(textStartsWith=selector_value)
            return el

    def _tap_center(self):
        x, y = self._duc.window_size()
        x_mid = x / 2
        y_mid = y / 2
        self._duc.touch.down(x_mid, y_mid)
        self._duc.touch.sleep(0.3)
        self._duc.touch.up(x_mid, y_mid)


if __name__ == "__main__":
    Duc = namedtuple("Duc", "serial_no imei android_ver model_name")
    sample_duc = Duc("23c44de9ec1e7ece", "4545454", "9", "model")
    duc1 = DucAutomator(sample_duc)
    duc1.scroll_to_text("About phone", match_type="contains")
    duc1.tap_by_text("About phone", match_type="contains")
