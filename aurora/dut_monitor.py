"""Set of classes that analyzes and capture connected DUTs (devices)"""
__author__ = "Jego Carlo Ramos, Sarah Opena"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

from threading import Thread
from time import sleep
from collections import namedtuple
import pyudev
import subprocess


class DutAuthFilter:
    """A utility class that filters and fetches
    authorized and un-authorized DUTs (devices)"""

    @classmethod
    def _get_serial_nums(cls):
        """Runs an adb subprocess command to get the authorized DUT Serial Numbers

        Returns:
            serial_nums (tuple): An immutable list of authorized serial numbers
        """
        adb_auth_key = "device"
        command = f"adb devices | grep {adb_auth_key}"
        result = cls._handle_value_error_and_result(cls._run_sub_process, command)
        if result:
            return cls.clean_up_for_serial_nums(adb_auth_key, result)
        else:
            return ()

    @classmethod
    def get_unauthorized_serial_nums(cls):
        """Runs an adb subprocess command to get the unauthorized DUT Serial Numbers

        Returns:
            unauthorized_serial_nums (tuple): An immutable list of unauthorized serial numbers
        """
        adb_not_auth_key = "unauthorized"
        command = f"adb devices | grep {adb_not_auth_key}"
        result = cls._handle_value_error_and_result(cls._run_sub_process, command)
        if result:
            return cls.clean_up_for_serial_nums(adb_not_auth_key, result)
        else:
            # Return an empty tuple if no un-authorized devices are found
            return ()

    @classmethod
    def _get_imei(cls, serial_no):
        """Get the IMEI of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            imei (str): The IMEI of the DUT
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
        """Returns the android version of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            android_ver (str): The android version of the DUT
        """
        command = f"adb -s {serial_no} shell getprop ro.build.version.release"
        return cls._handle_value_error_and_result(cls._run_sub_process, command)

    @classmethod
    def _get_model_name(cls, serial_no):
        """Returns the model name of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            model_name (str): The model (market) name of the DUT
        """
        command = f"adb -s {serial_no} shell getprop ro.product.model"
        return cls._handle_value_error_and_result(cls._run_sub_process, command)

    @classmethod
    def get_duts(cls):
        """Returns a list of authorized DUTs

        Returns:
            Dut (tuple of namedtuples): An immutable data object
        Raises:
            AssertionError: If the length of all DUT attrs are not equal
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
            raise AssertionError("The length of DUT attrs are not equal")

        # Create a list of DUT data objects
        Dut = namedtuple("Dut", "serial_no imei android_ver model_name")
        # Map every attr element to a single DUT data object
        auth_duts = [
            Dut(sn, imei, a_ver, m_name)
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
    def _handle_value_error_and_result(func, *args):
        """Handles the result and Value Error of a function the invokes a subprocess command
        Parameters:
            func (function) - The method to execute
            args (*args) - The parameters of the method to execute

        Returns:
            result (str) - The result of the function if valid
            result (None) - If the method raises a Value error
        """
        try:
            return func(*args)
        except ValueError:
            return None

    @staticmethod
    def clean_up_for_serial_nums(adb_auth_key, raw_text):
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
                # This effectively removes the "List of devices attached"
                if new_line_split.index(str_split) != 0:
                    # Get the serial no. part of "serial_no\tdevice" string
                    sn = str_split.split(adb_auth_key)[0].strip()
            else:
                # "List of devices attached" will not be included if the
                # adb_auth_key is "unauthorized"
                sn = str_split.split(adb_auth_key)[0].strip()

            # Check if the sn is truthy (not an empty string or None)
            if sn:
                serial_nums.append(sn)

        # Return a tuple of serial_nums
        return tuple(serial_nums)


class DutMonitor(Thread):
    """Represents a DUT (device) monitor running in the background"""

    def __init__(self):
        """Overrides the __init__ method of the Thread class"""
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
        print("Observing Devices...")
        # Run the initial check for already connected duts (devices) on start-up
        print(f"Authorized: {DutAuthFilter.get_duts()}")
        print(f"Unauthorized: {DutAuthFilter.get_unauthorized_serial_nums()}")
        for action, device in self.monitor:
            if action == "add":
                # print(f"Added: {device}")
                print("Device Added!")
                sleep(2)  # TODO (improve): adb needs some time to load. Ugly :(
                print(f"Authorized: {DutAuthFilter.get_duts()}")
                print(f"Unauthorized: {DutAuthFilter.get_unauthorized_serial_nums()}")

            elif action == "remove":
                # print(f"Removed: {device}")
                print("Device Removed!")
                sleep(0.2)  # TODO (improve): Paranoid about that small window :/
                print(f"Authorized: {DutAuthFilter.get_duts()}")
                print(f"Unauthorized: {DutAuthFilter.get_unauthorized_serial_nums()}")


if __name__ == "__main__":
    adm = DutMonitor()
    adm.start()
