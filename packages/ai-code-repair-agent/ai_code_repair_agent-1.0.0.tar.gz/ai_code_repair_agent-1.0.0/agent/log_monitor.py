import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_FILE_PATH = 'app.log'
ERROR_SIGNATURE = "Traceback (most recent call last):"

class LogChangeHandler(FileSystemEventHandler):

    def __init__(self, callback):
        self.callback = callback
        self.last_read_position = 0

    def on_modified(self, event):

        if not event.is_directory and event.src_path.endswith(LOG_FILE_PATH):
            logging.info(f"Detected a change in {LOG_FILE_PATH}")
            self.process_new_logs(event.src_path)

    def process_new_logs(self, file_path):

        try:
            with open(file_path, 'r') as f:
                f.seek(self.last_read_position)
                new_content = f.read()
                self.last_read_position = f.tell()

            if ERROR_SIGNATURE in new_content:
                logging.warning("Error signature detected in new log content!")
                self.callback(new_content)
        except IOError as e:
            logging.error(f"Error reading log file: {e}")


def start_monitoring(callback_on_error):

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    event_handler = LogChangeHandler(callback=callback_on_error)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    
    logging.info(f"Starting log monitor for file: {LOG_FILE_PATH}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Log monitor stopped.")
