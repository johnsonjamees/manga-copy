'''
This Python script is designed to monitor a specific directory for file changes, particularly focusing on files with a '.cbz' extension, commonly used for comic book archives.
Designed to make Suwayomi-Server and Kavita Work togethe. Might also work for Komga,

General Overview and Operation
Class Definition (MangaHandler): Inherits from FileSystemEventHandler to handle specific file system events—file creation and deletion.
Initialization: Accepts root_dir and target_dir specifying the directory to monitor and the target to store processed files, respectively.
Event Handling:
on_created: Triggered when a new file is created. If the file has a '.cbz' extension, it waits until the download is complete using wait_until_download_completes.
on_deleted: Triggered on file deletion. If the file is a '.cbz' file, it proceeds to remove the corresponding file in the target directory through remove_corresponding_file.
File Processing:
wait_until_download_completes: Checks repeatedly (every second) until the file size does not change, indicating the download has completed.
process_file: Changes the filename to include the series name (derived from the directory structure) and creates a hard link in the target directory.
remove_corresponding_file: Removes the hard link from the target directory if the original '.cbz' file is deleted.

How to run: 
screen -dmS manga-copy python3 /home/ubuntu/manga-copy.py
'''

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from concurrent.futures import ThreadPoolExecutor

class MangaHandler(FileSystemEventHandler):
    def __init__(self, root_dir, target_dir, max_workers=4):
        self.root_dir = root_dir
        self.target_dir = target_dir
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def on_created(self, event):
        if event.is_directory:
            return  # Ignore directories
        if event.src_path.endswith('.cbz'):
            # Submit file handling to the executor
            self.executor.submit(self.wait_until_download_completes, event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return  # Ignore directory deletions
        if event.src_path.endswith('.cbz'):
            # Submit file removal to the executor
            self.executor.submit(self.remove_corresponding_file, event.src_path)

    def wait_until_download_completes(self, file_path):
        """Wait until the file size stabilizes to consider it fully downloaded."""
        size = -1
        while True:
            new_size = os.path.getsize(file_path)
            if new_size == size:
                break  # File size has stabilized, download likely complete
            else:
                size = new_size
                time.sleep(1)  # Wait for 1 second before next check
        self.process_file(file_path)

    def process_file(self, file_path):
        path_parts = file_path.split(os.sep)
        if len(path_parts) < 4:
            return  # Not enough depth to be a series file

        series_name = path_parts[-2]
        file_name = path_parts[-1]
        new_file_name = f"{series_name} {file_name}"
        destination_path = os.path.join(self.target_dir, new_file_name)
        os.link(file_path, destination_path) # Creating a hard link instead of copying
        print(f"Hard link created from '{file_path}' to '{destination_path}'")

    def remove_corresponding_file(self, file_path):
        path_parts = file_path.split(os.sep)
        if len(path_parts) < 4:
            return # Not enough depth to be a series file

        series_name = path_parts[-2]
        file_name = path_parts[-1]
        deleted_file_name = f"{series_name} {file_name}"
        deleted_file_path = os.path.join(self.target_dir, deleted_file_name)

        if os.path.exists(deleted_file_path):
            os.remove(deleted_file_path) # Removing the hard link
            print(f"Hard link '{deleted_file_path}' removed in response to original file deletion")

def monitor_directory(root_dir, target_dir):
    event_handler = MangaHandler(root_dir, target_dir)
    observer = Observer()
    observer.schedule(event_handler, root_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    root_directory = '/home/ubuntu/mangas'
    target_directory = '/home/ubuntu/downloads'

    thread = threading.Thread(target=monitor_directory, args=(root_directory, target_directory))
    thread.start()
    thread.join()
