"""Set of classes that analyzes and capture connected Devices Under Customization (DUC)"""
__author__ = "Jego Carlo Ramos, Sarah Opena"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

from threading import Thread
from time import sleep
from collections import namedtuple
import pyudev
import subprocess

from helpers.logger import LoggerBuilder

logger_builder = LoggerBuilder("mayo", __name__)
logger = logger_builder.create_logger()


class DucAuthFilter:
    """A utility class that filters and fetches
    authorized and un-authorized DUCs"""

    @classmethod
    def _get_serial_nums(cls):
        """Runs an adb subprocess command to get the authorized DUC Serial Numbers

        Returns:
            serial_nums (tuple): An immutable list of authorized serial numbers
        """
        adb_auth_key = "device"
        command = f"adb devices | grep {adb_auth_key}"
        result = cls._handle_value_error_and_result(cls._run_sub_process, command)

        # Return the serial numbers if the result is truthy, else return an empty tuple
        return cls._clean_up_for_serial_nums(adb_auth_key, result) if result else ()

    @classmethod
    def get_unauthorized_serial_nums(cls):
        """Runs an adb subprocess command to get the unauthorized DUC Serial Numbers

        Returns:
            unauthorized_serial_nums (tuple): An immutable list of unauthorized serial numbers
        """
        adb_not_auth_key = "unauthorized"
        command = f"adb devices | grep {adb_not_auth_key}"
        result = cls._handle_value_error_and_result(cls._run_sub_process, command)

        # Return the serial numbers if the result is truthy, else return an empty tuple
        return cls._clean_up_for_serial_nums(adb_not_auth_key, result) if result else ()

    @classmethod
    def _get_imei(cls, serial_no):
        """Get the IMEI of a DUC

        Parameters:
            serial_no (str): The DUC's unique identifier
        Returns:
            imei (str): The IMEI of the DUC
        """
        command = (
            f"adb -s {serial_no} shell "
            + '"service call iphonesubinfo 1 | toybox cut -d \\"'
            + "'\\\""
            + "  -f2 | toybox grep -Eo '[0-9]' | toybox xargs | toybox sed 's/\\ //g'"
            + '"'
        )  # TODO (improve): This command is crazy
        return cls._handle_value_error_and_result(cls._run_sub_process, command)

    @classmethod
    def _get_android_ver(cls, serial_no):
        """Returns the android version of a DUC

        Parameters:
            serial_no (str): The DUC's unique identifier
        Returns:
            android_ver (str): The android version of the DUC
        """
        command = f"adb -s {serial_no} shell getprop ro.build.version.release"
        return cls._handle_value_error_and_result(cls._run_sub_process, command)

    @classmethod
    def _get_model_name(cls, serial_no):
        """Returns the model name of a DUC

        Parameters:
            serial_no (str): The DUC's unique identifier
        Returns:
            model_name (str): The model (market) name of the DUC
        """
        command = f"adb -s {serial_no} shell getprop ro.product.model"
        return cls._handle_value_error_and_result(cls._run_sub_process, command)

    @classmethod
    def get_ducs(cls):
        """Returns a list of authorized DUCs

        Returns:
            Duc (tuple of namedtuples): An immutable data object
        Raises:
            AssertionError: If the length of all DUC attrs are not equal
        """
        serial_nums = cls._get_serial_nums()

        # Get DUT attrs
        imeis = tuple([cls._get_imei(sn) for sn in serial_nums])
        android_vers = tuple([cls._get_android_ver(sn) for sn in serial_nums])
        model_names = tuple([cls._get_model_name(sn) for sn in serial_nums])

        # Check if every attr length are equal, raise an Assertion Error if not.
        # This could never (theoretically) happen as the methods that fetches
        # the attrs depend on the _get_serial_nums() method's immutable list return value.
        # An edge-case would be if one of adb shell commands' behavior changes at some point.
        length_list = [
            len(attr) for attr in (serial_nums, imeis, android_vers, model_names)
        ]
        if len(set(length_list)) != 1:
            raise AssertionError("The length of DUC attrs are not equal")

        # Create a tuple of DUC data objects
        Duc = namedtuple("Duc", "serial_no imei android_ver model_name")
        # Map the attr elements to DUC data objects
        auth_duts = [
            Duc(sn, imei, a_ver, m_name)
            for (sn, imei, a_ver, m_name) in zip(
                serial_nums, imeis, android_vers, model_names
            )
        ]

        return tuple(auth_duts)

    @staticmethod
    def _run_sub_process(command):
        """A utility method that runs a shell command subprocess

        Parameters:
            command (str): The shell command to run
        Returns:
            stdout (str): The standard out of the process
        Raises:
            ValueError: If the the subprocess does not produce an output
        """
        comp_proc = subprocess.run(command, capture_output=True, text=True, shell=True)
        # It's important to strip the stdout as it sometimes only return empty spaces
        res = comp_proc.stdout.strip()
        if not res:
            raise ValueError("The shell command did not produce an output")
        return res

    @staticmethod
    def _handle_value_error_and_result(sub_func, *args):
        """A utility method that handles the result and Value Error of a function
        the invokes a subprocess command

        Parameters:
            sub_func (function) - The subprocess method to execute
            args (*args) - The parameters of the method

        Returns:
            result (str) - The result of the subprocess function if valid
            result (None) - If the method raises a Value error
        """
        try:
            return sub_func(*args)
        except ValueError:
            return None

    @staticmethod
    def _clean_up_for_serial_nums(adb_auth_key, raw_text):
        """A utility method that returns the serial nums from the 'adb devices | grep <auth_key>' command

        Parameters:
            adb_auth_key (str) - The auth identifier associated with the serial_no
            raw_text (str) - The string to clean, it includes the serial numbers
        Returns:
            serial_nums (tuple of str) - The immutable list of serial numbers
        """
        serial_nums = []
        new_line_split = raw_text.split("\n")
        sn = None
        for str_split in new_line_split:
            if adb_auth_key == "device":
                # This effectively removes the "List of devices attached" element
                if new_line_split.index(str_split) != 0:
                    # Get the serial no. part of "serial_no\tdevice" string
                    sn = str_split.split(adb_auth_key)[0].strip()
            else:
                # "List of devices attached" will not be included if the
                # adb_auth_key is "unauthorized"
                sn = str_split.split(adb_auth_key)[0].strip()

            # Check if sn is truthy (not an empty string or None)
            if sn:
                serial_nums.append(sn)

        # Return a tuple of serial_nums
        return tuple(serial_nums)


class DucMonitor(Thread):
    """Represents a DUC monitor running in the background"""

    not_auth_checker_running = False

    def __init__(self, *listeners):
        """Overrides the __init__ method of the Thread class"""
        self.authorized_ducs = set()
        self.unauthorized_serial_nums = set()
        self.listeners = [listener for listener in listeners]

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
