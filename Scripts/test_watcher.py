"""
Simple test script to verify file system watching works
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TestHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"\n✅ FILE DETECTED: {event.src_path}")
            print(f"   File name: {Path(event.src_path).name}")
            print(f"   Time: {time.strftime('%H:%M:%S')}")

# Get the vault path
vault_path = Path(__file__).parent.parent
inbox_path = vault_path / 'Inbox'

print(f"Watching folder: {inbox_path}")
print(f"Folder exists: {inbox_path.exists()}")
print("\nDrop a file into Inbox/ to test...\n")

# Set up the observer
event_handler = TestHandler()
observer = Observer()
observer.schedule(event_handler, str(inbox_path), recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped")
    observer.stop()
observer.join()
