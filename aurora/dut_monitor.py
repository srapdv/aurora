from threading import Thread
from time import sleep
from collections import namedtuple
import pyudev
import subprocess


class DutAuthFilter:
    """Represents a gate that observes and filters
    authorized and un-authorized duts (devices)"""

    duts = namedtuple("Dut", "id imei android_version model_name")
    dut_ids = ()

    @classmethod
    def _get_dut_ids(cls):
        """Run an adb subprocess command to get authorized duts"""
        command_1 = ("adb", "devices")
        command_2 = ("grep", "device")
        to_pipe_out = subprocess.run(command_1, capture_output=True, text=True)
        raw_text = subprocess.run(
            command_2, capture_output=True, text=True, input=to_pipe_out.stdout
        )
        current_ids = []
        new_line_split = raw_text.stdout.split("\n")
        for str_split in new_line_split:
            # This effectively removes the "List of devices attached"
            if new_line_split.index(str_split) != 0:
                # Get the id part of "random_id\tdevice" string
                id = str_split.split("\t")[0]
                # Check if the id is truthy (not an empty string)
                if id:
                    current_ids.append(id)
        # Pass the local ids to the class attr by value
        cls.dut_ids = tuple(current_ids[:])
        print(cls.dut_ids)


class DutMonitor(Thread):
    """Represents a dut (device) monitor running in the background"""

    def __init__(self):
        """Override the Thread's __init__ method"""
        context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(context)
        self.monitor.filter_by(subsystem="tty")
        # This is how you call the Thread's __init__() method in Python 3
        super().__init__()

    def run(self):
        """Override the Thread's run method"""
        print("Observing Devices...")
        # Run the initial check for already connected duts (devices) on start-up
        DutAuthFilter._get_dut_ids()
        for action, device in self.monitor:
            if action == "add":
                print(f"Added: {device}")
                sleep(2)  # TODO (improve): adb needs some time to load. Ugly :(
                DutAuthFilter._get_dut_ids()

            elif action == "remove":
                print(f"Removed: {device}")
                sleep(0.2)  # TODO (improve): Paranoid about that small window :/
                DutAuthFilter._get_dut_ids()


if __name__ == "__main__":
    adm = DutMonitor()
    adm.start()
