"""Set of classes that analyzes and capture connected
Devices Under Customization (DUC)

Classes:
    DucMonitor
Misc Variables:
    __author__
    __copyright__
    __maintainer__
    logger_builder
    logger
"""
__author__ = "Jego Carlo Ramos, Sarah Opena"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

from threading import Thread
from time import sleep
import pyudev

from helpers.logger import LoggerBuilder
from helpers.duc_auth_filter import DucAuthFilter
from helpers.duc_listener import DucListener

logger_builder = LoggerBuilder("stonehenge", __name__)
logger = logger_builder.create_logger()


# TODO: Propose this class to be a Singleton
class DucMonitor(Thread):
    """Represents a DUC monitor running in the background"""

    not_auth_checker_running = False

    def __init__(self, *listeners):
        """Overrides the __init__ method of the Thread class
        Parameters:
            listeners (DucListener) - arbitrary number of listeners
        """
        self.authorized_ducs = set()
        self.unauthorized_serial_nums = set()
        # self.listeners = [listener for listener in listeners]

        # Check if listeners implemented the required interface
        self.listeners = []
        for listener in listeners:
            if not isinstance(listener, DucListener):
                msg = f"Ignored {str(listener)} because it is not a child of {DucListener.__name__}"
                logger.error(msg)
            else:
                self.listeners.append(listener)

        # Attrs for pyudev
        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context)
        self.monitor.filter_by(subsystem="tty")

        # The Python3 way of calling the Thread's __init__() method
        # Ref: https://www.bogotobogo.com/python/Multithread/python_multithreading_subclassing_creating_threads.php
        # Alternatives: Thread.__init__(self) or super(DutMonitor, self).__init__()
        super().__init__()
        # Kill this thread if the Main thread stops
        self.daemon = True

    def run(self):
        """Overrides the run() method of the Thread class"""
        logger.debug("DUC Monitor running...")

        # Run the initial check for already connected DUCs on start-up
        self._handle_added_ducs()
        self._handle_unauthorized_ducs()

        for action, device in self.monitor:
            if action == "add":
                logger.debug("Device Added!")

                # TODO (improve): ADB needs some time to discover the DUC. Ugly :(
                sleep(2)

                self._handle_added_ducs()
                self._handle_unauthorized_ducs()

            elif action == "remove":
                logger.debug("Device Removed!")

                # TODO (improve): Paranoid about that small window :/
                sleep(0.2)

                self._handle_removed_ducs()

    def _handle_added_ducs(self):
        """Sends the added DUCs to listeners"""
        new_duc_batch = DucAuthFilter.get_ducs()
        for duc in new_duc_batch:
            # Filter only newly plugged DUCs
            if duc not in self.authorized_ducs:
                # Add the new DUC to the authorized set
                self.authorized_ducs.add(duc)
                # Send the DUC to all listeners
                for listener in self.listeners:
                    logger.debug(f"Sending {duc} to {listener}")
                    listener.add_duc(duc)

    def _handle_removed_ducs(self):
        """Removes DUCs from all listeners"""
        new_duc_batch = set(DucAuthFilter.get_ducs())
        # Check for the removed DUCs
        removed_ducs = self.authorized_ducs.difference(new_duc_batch)
        if removed_ducs:
            self.authorized_ducs = new_duc_batch
            # Remove DUCs from all lisneters
            for duc in removed_ducs:
                for listener in self.listeners:
                    logger.debug(f"Removing {duc} from {listener}")
                    listener.remove_duc(duc)

    def _handle_unauthorized_ducs(self):
        """Long-poll while there are un-authorized DUCs"""

        # Only invoke once
        if DucMonitor.not_auth_checker_running:
            return

        long_poll_sec = 3
        # Check for unauthorized DUCs
        unauthorized_ducs = DucAuthFilter.get_unauthorized_serial_nums()
        if unauthorized_ducs:
            DucMonitor.not_auth_checker_running = True
            # Long poll for every <long_poll_sec> seconds
            while DucMonitor.not_auth_checker_running:
                logger.debug(f"Some DUCs are not authorized: {unauthorized_ducs}")
                # The Device Authorization dialog takes about this long to show up
                sleep(long_poll_sec)
                self._handle_added_ducs()
                unauthorized_ducs = DucAuthFilter.get_unauthorized_serial_nums()
                if not unauthorized_ducs:
                    DucMonitor.not_auth_checker_running = False


if __name__ == "__main__":
    dm = DucMonitor()
    dm.start()
