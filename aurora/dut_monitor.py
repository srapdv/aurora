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
    """Represents a gate that observes and filters
    authorized and un-authorized DUTs (devices)"""

    authorized_duts = []
    unauthorized_duts = []

    @staticmethod
    def _run_sub_process(command):
        """Runs a shell command subprocess

        Parameters:
            command (str): The shell command to run
        Returns:
            stdout (str): The standard out of the process
        Raises:
            ValueError: If the the subprocess does not produce an output
        """
        comp_proc = subprocess.run(command, capture_output=True, text=True, shell=True)
        res = comp_proc.stdout
        if not res:
            raise ValueError("The shell command did not produce an output")
        return res

    @classmethod
    def _get_serial_nums(cls):
        """Runs an adb subprocess command to get the authorized DUT Serial Numbers

        Returns:
            serial_nums (tuple): An immutable list of authorized serial numbers
        """
        command = "adb devices | grep device"
        raw_text = cls._run_sub_process(command)
        current_serial_nums = []
        new_line_split = raw_text.split("\n")
        for str_split in new_line_split:
            # This effectively removes the "List of devices attached"
            if new_line_split.index(str_split) != 0:
                # Get the serial no. part of "serial_no\tdevice" string
                sn = str_split.split("device")[0].strip()
                # Check if the sn is truthy (not an empty string)
                if sn:
                    current_serial_nums.append(sn)
        # Return a copy (by value) of serial_nums
        return tuple(current_serial_nums[:])

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
        raw_text = cls._run_sub_process(command)
        return raw_text.strip()

    @classmethod
    def _get_android_ver(cls, serial_no):
        """Returns the android version of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            android_ver (str): The android version of the DUT
        """
        command = f"adb -s {serial_no} shell getprop ro.build.version.release"
        raw_text = cls._run_sub_process(command)
        return raw_text.strip()

    @classmethod
    def _get_model_name(cls, serial_no):
        """Returns the android version of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            model_name (str): The model (market) name of the DUT
        """
        command = f"adb -s {serial_no} shell getprop ro.product.model"
        raw_text = cls._run_sub_process(command)
        return raw_text.strip()

    @classmethod
    def get_duts(cls):
        """Returns a list of authorized DUTs

        Returns:
            Dut (namedtuple): An immutable data object
        Raises:
            AssertionError: If the length of all DUT attrs are not equal
        """
        serial_nums = cls._get_serial_nums()

        # Get DUT attrs
        imeis = tuple([cls._get_imei(sn) for sn in serial_nums])
        android_vers = tuple([cls._get_android_ver(sn) for sn in serial_nums])
        model_names = tuple([cls._get_model_name(sn) for sn in serial_nums])

        # Check if every attr length are equal. Raise an Assertion Error if not.
        # This could never (theoretically) happen as the methods that fetches
        # the attrs depend on the _get_serial_nums() immutable list return value.
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
        cls.authorized_duts = auth_duts[:]

        print(cls.authorized_duts)


class DutMonitor(Thread):
    """Represents a dut (device) monitor running in the background"""

    def __init__(self):
        """Overrides the Thread's __init__ method"""
        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context)
        self.monitor.filter_by(subsystem="tty")
        # The Python3 way of calling the Thread's __init__() method
        # Ref: https://www.bogotobogo.com/python/Multithread/python_multithreading_subclassing_creating_threads.php
        # Alternatives: Thread.__init__(self) or super(DutMonitor, self).__init__()
        super().__init__()

    def run(self):
        """Overrides the Thread's run method"""
        print("Observing Devices...")
        # Run the initial check for already connected duts (devices) on start-up
        DutAuthFilter.get_duts()
        for action, device in self.monitor:
            if action == "add":
                print(f"Added: {device}")
                sleep(2)  # TODO (improve): adb needs some time to load. Ugly :(
                DutAuthFilter.get_duts()

            elif action == "remove":
                print(f"Removed: {device}")
                sleep(0.2)  # TODO (improve): Paranoid about that small window :/
                DutAuthFilter.get_duts()


if __name__ == "__main__":
    adm = DutMonitor()
    adm.start()
