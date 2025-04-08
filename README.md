This Python script is designed to monitor a specific directory for file changes, particularly focusing on files with a `.cbz` extension, commonly used for comic book archives.
Designed to make Suwayomi-Server and Kavita Work together. Might also work for Komga

#### General Overview and Operation:
- Class Definition (MangaHandler): Inherits from `FileSystemEventHandler` to handle specific file system events—file creation and deletion.
- Initialization: Accepts `root_dir` and `target_dir` specifying the directory to monitor and the target to store processed files, respectively.
##### Event Handling:
- `on_created`: Triggered when a new file is created. If the file has a `.cbz` extension, it waits until the download is complete using `wait_until_download_completes`.
- `on_deleted`: Triggered on file deletion. If the file is a `.cbz` file, it proceeds to remove the corresponding file in the target directory through `remove_corresponding_file`.
##### File Processing:
- `wait_until_download_completes`: Checks repeatedly (every second) until the file size does not change, indicating the download has completed.
- `process_file`: Changes the filename to include the series name (derived from the directory structure) and creates a hard link in the target directory.
- `remove_corresponding_file`: Removes the hard link from the target directory if the original `.cbz` file is deleted.

##### How to run: 
```
screen -dmS manga-copy python3 /home/ubuntu/manga-copy.py
```
