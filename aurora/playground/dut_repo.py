import threading
import pyudev
import time
import concurrent.futures
import subprocess


class DutAuthFlagger:
    @staticmethod
    def _get_dut_ids():
        command_1 = ("adb", "devices")
        command_2 = ("grep", "device")
        to_pipe_out = subprocess.run(command_1, capture_output=True, text=True)
        raw_text = subprocess.run(
            command_2, capture_output=True, text=True, input=to_pipe_out.stdout
        )

        new_line_split = raw_text.stdout.split("\t")
        print(new_line_split)


if __name__ == "__main__":
    DutAuthFlagger._get_dut_ids()

# start = time.perf_counter()


# def do_something(seconds):
#     print(f"Sleeping for {seconds} second")
#     try:
#         time.sleep(seconds)
#     except TypeError:
#         print("Must be a number")
#     else:
#         return f"Done na me {seconds}"


# with concurrent.futures.ThreadPoolExecutor() as executer:
#     seconds = [3.2, 4.3, 1, 2]
#     results = executer.map(do_something, seconds)
#     for result in results:
#         print(result)
# execs = [executer.submit(do_something, sec) for sec in seconds]
# for exec in concurrent.futures.as_completed(execs):
#     print(exec.result())

# threads = []
# for _ in range(10):
#     t = threading.Thread(target=do_something, args=[2])
#     t.start()
#     threads.append(t)

# for t in threads:
#     t.join()

# finish = time.perf_counter()

# time_took = round(finish - start, 5)
# print(f"Time finished: {time_took} seconds")

# class AndroidDeviceMonitor(threading.Thread):
#     def __init__(self):
#         self.context = pyudev.Context()
#         self.monitor = pyudev.Monitor.from_netlink(self.context)
#         self.monitor.filter_by(subsystem="tty")
#         self.listeners = []

#         threading.Thread.__init__(self)

#     def run(self):
#         ("Checking devices..")
#         for action, device in self.monitor:
#             if action == "add":
#                 print(device)
#                 for listener in self.listeners:
#                     listener.add_device(
#                         device.get("ID_SERIAL_SHORT"), device.get("ID_MODEL"), "9.0"
#                     )
#                     # logger.debug('Device {} has been added.'
#                     #     .format(device.get('ID_SERIAL_SHORT')))
#             elif action == "remove":
#                 for listener in self.listeners:
#                     listener.remove_device(
#                         device.get("ID_SERIAL_SHORT"), device.get("ID_MODEL"), "9.0"
#                     )
#                     # logger.debug('Device {} has been removed.'.format(device.get('ID_SERIAL_SHORT')))

#     def add_listener(self, listener):
#         self.listeners.append(listener)


# if __name__ == "__main__":
#     adm = AndroidDeviceMonitor()
#     adm.start()
# def start():
#     context = pyudev.Context()
#     monitor = pyudev.Monitor.from_netlink(context)
#     monitor.filter_by(subsystem="tty")
#     monitor.start()

#     for device in iter(monitor.poll, None):
#         if device.action == "add":
#             print("device connected")
#             print(device.get("ID_SERIAL_SHORT"))
#         elif device.action == "remove":
#             print("device removed")
#             print(device)


# start()
