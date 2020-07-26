import concurrent.futures
from threading import Lock
from time import sleep


class Database:
    def __init__(self):
        self.tasks = []
        self._lock = Lock()

    def update(self, task_name, seconds):
        sleep(seconds)
        self.tasks.append(task_name)
        # with self._lock:
        #     local_val = self.value
        #     local_val += 1
        #     sleep(seconds)
        #     self.value = local_val
        return task_name

    def get(self):
        return self.tasks


if __name__ == "__main__":
    res = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        work_orders = (("mine", 3), ("build", 1), ("shout", 1.7))
        db = Database()
        futures = [executor.submit(db.update, wo[0], wo[1]) for wo in work_orders]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            # print(future.result())
            # res.append(future.result())
    print(db.get())
