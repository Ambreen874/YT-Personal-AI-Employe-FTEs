"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
All watchers follow the same pattern: monitor inputs → create action files.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all AI Employee watchers.
    
    Watchers are lightweight Python scripts that run continuously,
    monitoring various inputs and creating actionable .md files
    for Claude to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: How often to check for updates (in seconds)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Setup logging
        self.log_dir = self.vault_path / 'Logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = self.log_dir / f'watcher_{self.__class__.__name__}_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure required directories exist
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        directories = [
            self.needs_action,
            self.vault_path / 'Done',
            self.vault_path / 'Plans',
            self.vault_path / 'Logs',
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process.
        
        Returns:
            List of new items that need action
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if creation failed
        """
        pass
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        This method runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s) to process')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                if filepath:
                                    self.logger.info(f'Created action file: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}', exc_info=True)
                    else:
                        self.logger.debug('No new items found')
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise
    
    def get_timestamp(self) -> str:
        """Get current ISO format timestamp."""
        return datetime.now().isoformat()
    
    def get_date_string(self) -> str:
        """Get current date string for filenames."""
        return datetime.now().strftime('%Y-%m-%d')
    
    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use in filenames.
        
        Args:
            name: The original name
            
        Returns:
            Sanitized filename-safe string
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()
