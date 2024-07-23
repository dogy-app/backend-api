import os
import sys
import time
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkerReloader(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.start_worker()

    def start_worker(self):
        if self.process:
            self.process.kill()
            logger.info(f"Worker with PID {self.process.pid} killed.")
        self.process = subprocess.Popen([sys.executable, self.script_path])
        logger.info(f"Started worker with PID {self.process.pid}")

    def on_modified(self, event):
        logger.info(f"File modified: {event.src_path}")
        if event.src_path.endswith(os.path.basename(self.script_path)):
            logger.info(f"{self.script_path} modified; restarting worker...")
            self.start_worker()

if __name__ == "__main__":
    worker_script = "workers.py"
    script_dir = os.path.dirname(os.path.abspath(worker_script))
    logger.info(f"Monitoring changes in directory: {script_dir} for script: {worker_script}")

    event_handler = WorkerReloader(worker_script)
    observer = Observer()
    observer.schedule(event_handler, path=script_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
