import contextlib
import csv
import platform
import sys
import threading
import time
from pathlib import Path

import psutil
import shutil


class Timer:
    def __init__(self, output=None):
        self._results = []
        self._output = output

    @contextlib.contextmanager
    def measure(self, name):
        start = time.time()
        yield
        end = time.time()

        self._results.append((end, name, end - start))

    def dump(self):
        if self._output is None:
            print(self._results)
            return

        with open(self._output, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'name', 'elapsed'])
            for item in self._results:
                writer.writerow(item)


class PerformanceWatcher(threading.Thread):
    def __init__(self, on_report=None, interval=5):
        super().__init__()
        self.running = threading.Event()
        self.on_report = on_report
        self.interval = interval

    # NOTE: Use start() to start the thread, this method is a new thread starting point
    def run(self):
        print('PerformanceWatcher starting...')
        self.running.set()
        print("PerformanceWatcher started.")
        last_report_time = None
        while self.running.is_set():
            if last_report_time is None or (time.time() - last_report_time) > self.interval:
                disk_total, disk_used, disk_free = shutil.disk_usage(Path(__file__).absolute())
                report = {
                    "cpu": psutil.cpu_percent(),
                    "ram": psutil.virtual_memory().percent,
                    "disk": disk_used / disk_total,
                    "app_uptime": time.process_time(),
                    "device_uptime": time.time() - psutil.boot_time(),
                    "os_name": platform.system(),
                    "os_version": platform.release(),
                    "python_version": sys.version
                }
                if self.on_report is not None:
                    self.on_report(report)
                last_report_time = time.time()
            else:
                time.sleep(1)

    def stop(self):
        print('PerformanceWatcher stopping...')
        self.running.clear()

if __name__ == '__main__':
    pw = PerformanceWatcher()
    pw.start()
    start = time.time()
    time.sleep(5)
    pw.stop()