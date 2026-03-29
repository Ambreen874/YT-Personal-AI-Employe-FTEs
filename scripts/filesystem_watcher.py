"""
File System Watcher Module

Monitors a drop folder for new files and creates action files
for the AI Employee to process.

This is the simplest watcher - users can drop any file into the
Inbox folder and the AI will process it.
"""

import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    """
    Handles file system events for the drop folder.
    When a new file is created, it gets copied to Needs_Action
    with accompanying metadata.
    """
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        """
        Initialize the handler.
        
        Args:
            watcher: The parent FileSystemWatcher instance
        """
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: The file system event
        """
        if event.is_directory:
            return
        
        source_path = Path(event.src_path)
        
        # Ignore temporary files
        if source_path.name.startswith('~$') or source_path.suffix in ['.tmp', '.part']:
            self.logger.debug(f'Ignoring temporary file: {source_path.name}')
            return
        
        self.logger.info(f'New file detected: {source_path.name}')
        
        try:
            # Process the file
            self.watcher.process_file(source_path)
        except Exception as e:
            self.logger.error(f'Error processing file {source_path.name}: {e}', exc_info=True)


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When a file is dropped into the Inbox folder, it creates
    an action file in Needs_Action with metadata about the file.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: How often to check (in seconds, minimum 5)
        """
        super().__init__(vault_path, max(check_interval, 5))
        
        # Setup drop folder
        self.drop_folder = self.vault_path / 'Inbox'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files to avoid duplicates
        self.processed_files: Dict[str, str] = {}  # filename -> file hash
        self._load_processed_files()
        
        # Setup observer
        self.observer: Optional[Observer] = None
    
    def _load_processed_files(self):
        """Load the list of already processed files."""
        cache_file = self.vault_path / 'Logs' / 'processed_files.txt'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    for line in f:
                        if ' :: ' in line:
                            filename, file_hash = line.strip().split(' :: ', 1)
                            self.processed_files[filename] = file_hash
            except Exception as e:
                self.logger.warning(f'Could not load processed files cache: {e}')
    
    def _save_processed_file(self, filename: str, file_hash: str):
        """Save a processed file to the cache."""
        cache_file = self.vault_path / 'Logs' / 'processed_files.txt'
        with open(cache_file, 'a') as f:
            f.write(f'{filename} :: {file_hash}\n')
    
    def _calculate_hash(self, filepath: Path) -> str:
        """
        Calculate SHA256 hash of a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Hex digest of the file hash
        """
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def process_file(self, source_path: Path):
        """
        Process a newly dropped file.
        
        Args:
            source_path: Path to the source file
        """
        filename = source_path.name
        
        # Check if already processed
        if filename in self.processed_files:
            self.logger.debug(f'File already processed: {filename}')
            return
        
        # Calculate file hash
        try:
            file_hash = self._calculate_hash(source_path)
        except Exception as e:
            self.logger.error(f'Could not calculate hash for {filename}: {e}')
            return
        
        # Copy file to Needs_Action
        dest_path = self.needs_action / f'FILE_{filename}'
        
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            self.logger.info(f'Copied file to {dest_path}')
        except Exception as e:
            self.logger.error(f'Could not copy file: {e}')
            return
        
        # Create metadata file
        self.create_action_file({
            'filename': filename,
            'source_path': str(source_path),
            'dest_path': str(dest_path),
            'size': source_path.stat().st_size,
            'hash': file_hash
        })
        
        # Mark as processed
        self.processed_files[filename] = file_hash
        self._save_processed_file(filename, file_hash)
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of new file paths to process
        """
        new_files = []
        
        try:
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    
                    # Skip already processed
                    if filename in self.processed_files:
                        continue
                    
                    # Skip temporary files
                    if filename.startswith('~$') or file_path.suffix in ['.tmp', '.part']:
                        continue
                    
                    new_files.append(file_path)
        except Exception as e:
            self.logger.error(f'Error scanning drop folder: {e}')
        
        return new_files
    
    def create_action_file(self, item: dict) -> Optional[Path]:
        """
        Create a metadata action file for the dropped file.
        
        Args:
            item: Dictionary containing file information
            
        Returns:
            Path to the created metadata file
        """
        filename = self.sanitize_filename(item['filename'])
        timestamp = self.get_date_string()
        
        metadata_path = self.needs_action / f'FILE_{filename}.meta.md'
        
        content = f'''---
type: file_drop
original_name: {item['filename']}
dropped_date: {self.get_timestamp()}
size: {item['size']} bytes
file_hash: {item['hash']}
status: pending
---

# File Dropped for Processing

**Original Name:** {item['filename']}

**Size:** {item['size']} bytes

**Location:** `{item['dest_path']}`

---

## Suggested Actions

- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Take any required action
- [ ] Move to /Done when complete

---

*Created by FileSystemWatcher*
'''
        
        try:
            metadata_path.write_text(content, encoding='utf-8')
            self.logger.info(f'Created metadata file: {metadata_path.name}')
            return metadata_path
        except Exception as e:
            self.logger.error(f'Could not create metadata file: {e}')
            return None
    
    def run(self):
        """
        Main run loop using watchdog observer.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Drop folder: {self.drop_folder}')
        
        # First, scan for existing files
        self.logger.info('Scanning for existing files in drop folder...')
        files = self.check_for_updates()
        for file_path in files:
            self.process_file(file_path)
        
        # Setup watchdog observer
        event_handler = FileDropHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        self.observer.start()
        
        self.logger.info(f'Watching for new files in {self.drop_folder}')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
            self.observer.stop()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            self.observer.stop()
        
        self.observer.join()
        self.logger.info('Observer stopped')


def main():
    """Entry point for running the file system watcher."""
    import sys
    
    # Default vault path
    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        print('Usage: python filesystem_watcher.py [vault_path]')
        sys.exit(1)
    
    watcher = FileSystemWatcher(str(vault_path))
    watcher.run()


if __name__ == '__main__':
    main()
