"""
File System Watcher Module

Monitors a drop folder for new files and creates action files in the
Needs_Action folder for the AI Employee to process.

This is the simplest watcher to set up and is perfect for the Bronze tier.
Users can drop any file (documents, images, etc.) into the Inbox folder,
and the watcher will create corresponding action files.
"""

import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """
    Handles file system events for the drop folder.
    
    When a new file is created, it creates a corresponding .md action file
    in the Needs_Action folder.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the handler.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.processed_files = set()
        
        # Ensure folders exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
    
    def on_created(self, event):
        """
        Handle file creation events.

        Args:
            event: FileSystemEvent object
        """
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip hidden files and temporary files
        if source.name.startswith('.') or source.suffix in ['.tmp', '.swp']:
            return
        
        # Skip if already processed
        file_hash = self._get_file_hash(source)
        if file_hash in self.processed_files:
            return
        
        print(f'\n[FileSystemWatcher] 📁 FILE DETECTED: {source.name}')
        print(f'[FileSystemWatcher]    Path: {source}')
        print(f'[FileSystemWatcher]    Size: {self._format_size(source.stat().st_size)}')
        
        self._process_file(source)
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Get a hash of the file for tracking."""
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception:
            return str(filepath)
    
    def _process_file(self, source: Path):
        """
        Process a new file and create an action file.
        
        Args:
            source: Path to the source file
        """
        # Create metadata file
        meta_path = self.needs_action / f'FILE_{source.name}.md'
        
        content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
created: {time.strftime('%Y-%m-%dT%H:%M:%S')}
priority: medium
status: pending
---

# New File Dropped for Processing

## File Details
- **Original Name**: {source.name}
- **Size**: {self._format_size(source.stat().st_size)}
- **Location**: {source.parent}
- **Detected**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file (document, image, data, other)
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
Add any notes or context about this file here.
'''
        
        meta_path.write_text(content)
        self.processed_files.add(self._get_file_hash(source))
        print(f'[FileSystemWatcher] Created action file for: {source.name}')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


class FileSystemWatcher(BaseWatcher):
    """
    File System Watcher using watchdog.
    
    Monitors the Inbox folder for new files and creates action files
    in the Needs_Action folder.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Check interval (not used with watchdog, but kept for API compatibility)
        """
        super().__init__(vault_path, check_interval)
        self.inbox = self.vault_path / 'Inbox'
        self.inbox.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self) -> list:
        """
        This method is not used with watchdog (it's event-driven).
        Included for API compatibility with BaseWatcher.
        
        Returns:
            list: Empty list (watchdog handles events directly)
        """
        return []
    
    def create_action_file(self, item) -> Path:
        """
        This method is not used with watchdog (handled by DropFolderHandler).
        Included for API compatibility with BaseWatcher.
        
        Args:
            item: Not used
            
        Returns:
            Path: None
        """
        pass
    
    def run(self):
        """
        Run the file system watcher using watchdog Observer.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Watching folder: {self.inbox}')
        
        event_handler = DropFolderHandler(str(self.vault_path))
        observer = Observer()
        observer.schedule(event_handler, str(self.inbox), recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        observer.join()


if __name__ == '__main__':
    import sys
    
    # Default to current directory if no vault path provided
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1]).resolve()
    else:
        vault_path = Path.cwd().resolve()
    
    print(f'[FileSystemWatcher] Starting...')
    print(f'[FileSystemWatcher] Vault path: {vault_path}')
    print(f'[FileSystemWatcher] Watching: {vault_path / "Inbox"}')
    print(f'[FileSystemWatcher] Press Ctrl+C to stop')
    
    watcher = FileSystemWatcher(str(vault_path))
    watcher.run()
