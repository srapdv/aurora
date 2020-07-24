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
        """
        comp_proc = subprocess.run(command, capture_output=True, text=True, shell=True)
        return comp_proc.stdout

    @classmethod
    def _get_ids(cls):
        """Runs an adb subprocess command to get the authorized DUT IDs

        Returns:
            ids (tuple): An immutable list of authorized devices
        """
        command = "adb devices | grep device"
        raw_text = cls._run_sub_process(command)
        current_ids = []
        new_line_split = raw_text.split("\n")
        for str_split in new_line_split:
            # This effectively removes the "List of devices attached"
            if new_line_split.index(str_split) != 0:
                # Get the id part of "random_id\tdevice" string
                id = str_split.split("device")[0].strip()
                # Check if the id is truthy (not an empty string)
                if id:
                    current_ids.append(id)
        # Return  local ids
        return tuple(current_ids[:])

    @classmethod
    def _get_serial_no(cls, id):
        """Returns the android version of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            model_name (str): The model (market) name of the DUT
        Notes:
            Some DUT models, specifically newer ones, will have their SN
            equal to their DUT ID. Older ones won't have this attribute
            equality.
        """
        command = f"adb -s {id} shell getprop ro.boot.serialno"
        raw_text = cls._run_sub_process(command)
        return raw_text.strip()

    @classmethod
    def _get_imei(cls, id):
        """Get the IMEI of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            imei (str): The IMEI of the DUT
        """
        command = (
            f"adb -s {id} shell "
            + '"service call iphonesubinfo 1 | toybox cut -d \\"'
            + "'\\\""
            + "  -f2 | toybox grep -Eo '[0-9]' | toybox xargs | toybox sed 's/\\ //g'"
            + '"'
        )  # TODO (improve): This command is crazy
        raw_text = cls._run_sub_process(command)
        return raw_text.strip()

    @classmethod
    def _get_android_ver(cls, id):
        """Returns the android version of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            android_ver (str): The android version of the DUT
        """
        command = f"adb -s {id} shell getprop ro.build.version.release"
        raw_text = cls._run_sub_process(command)
        return raw_text.strip()

    @classmethod
    def _get_model_name(cls, id):
        """Returns the android version of a DUT

        Parameters:
            id (str): The DUT ID
        Returns:
            model_name (str): The model (market) name of the DUT
        """
        command = f"adb -s {id} shell getprop ro.product.model"
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
        ids = cls._get_ids()
        # Get DUT attrs
        serial_nums = tuple([cls._get_serial_no(id) for id in ids])
        imeis = tuple([cls._get_imei(id) for id in ids])
        android_vers = tuple([cls._get_android_ver(id) for id in ids])
        model_names = tuple([cls._get_model_name(id) for id in ids])

        # Check if every attr length are equal. Raise an Assertion Error if not.
        # This could never (theoretically) happen as the methods that fetches
        # the attrs depend on the _get_ids() immutable list return value.
        # An edge-case would be if one of adb shell commands' behavior changes at some point.
        length_list = [
            len(attr) for attr in (ids, imeis, android_vers, model_names, serial_nums)
        ]
        if len(set(length_list)) != 1:
            raise AssertionError("The length of DUT attrs are not equal")

        # Create a list of DUT data objects
        Dut = namedtuple("Dut", "id serial_no imei android_ver model_name")
        # Map every attr element to a single DUT data object
        auth_duts = [
            Dut(id, sn, imei, a_ver, m_name)
            for (id, sn, imei, a_ver, m_name) in zip(
                ids, serial_nums, imeis, android_vers, model_names,
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
