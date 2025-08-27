"""
File system watching for automatic rule reloading
"""

import logging
import threading
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
from watchdog.observers import Observer

from .config import ServerConfig


logger = logging.getLogger(__name__)


class RuleFileHandler(FileSystemEventHandler):
    """Handler for rule file system events."""
    
    def __init__(self, reload_callback: Callable[[], None], debounce_seconds: float = 1.0):
        """Initialize the file handler."""
        super().__init__()
        self.reload_callback = reload_callback
        self.debounce_seconds = debounce_seconds
        self._last_reload_time = 0
        self._reload_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._is_rule_file(event.src_path):
            logger.debug(f"Rule file modified: {event.src_path}")
            self._schedule_reload()
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._is_rule_file(event.src_path):
            logger.debug(f"Rule file created: {event.src_path}")
            self._schedule_reload()
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and self._is_rule_file(event.src_path):
            logger.debug(f"Rule file deleted: {event.src_path}")
            self._schedule_reload()
    
    def _is_rule_file(self, file_path: str) -> bool:
        """Check if the file is a rule file (.md extension)."""
        return Path(file_path).suffix.lower() == '.md'
    
    def _schedule_reload(self):
        """Schedule a debounced reload."""
        with self._lock:
            # Cancel existing timer if any
            if self._reload_timer:
                self._reload_timer.cancel()
            
            # Schedule new reload
            self._reload_timer = threading.Timer(self.debounce_seconds, self._execute_reload)
            self._reload_timer.start()
    
    def _execute_reload(self):
        """Execute the reload callback."""
        try:
            current_time = time.time()
            if current_time - self._last_reload_time >= self.debounce_seconds:
                logger.info("Executing rule reload due to file changes")
                self.reload_callback()
                self._last_reload_time = current_time
        except Exception as e:
            logger.error(f"Error during rule reload: {e}")
    
    def stop(self):
        """Stop any pending reload timers."""
        with self._lock:
            if self._reload_timer:
                self._reload_timer.cancel()
                self._reload_timer = None


class FileWatcher:
    """Watches rule files for changes and triggers reloads."""
    
    def __init__(self, config: ServerConfig, reload_callback: Callable[[], None]):
        """Initialize the file watcher."""
        self.config = config
        self.reload_callback = reload_callback
        self.observer: Optional[Observer] = None
        self.handler: Optional[RuleFileHandler] = None
        self._running = False
        
        logger.info(f"Initialized FileWatcher for directory: {config.rules_directory}")
    
    def start(self) -> bool:
        """Start watching for file changes."""
        if not self.config.watch_files:
            logger.info("File watching is disabled in configuration")
            return False
        
        if self._running:
            logger.warning("File watcher is already running")
            return True
        
        try:
            rules_path = self.config.rules_path
            
            # Create directory if it doesn't exist
            if not rules_path.exists():
                rules_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created rules directory: {rules_path}")
            
            # Create handler and observer
            self.handler = RuleFileHandler(self.reload_callback)
            self.observer = Observer()
            
            # Start watching the rules directory
            self.observer.schedule(self.handler, str(rules_path), recursive=False)
            self.observer.start()
            
            self._running = True
            logger.info(f"Started file watcher for: {rules_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop watching for file changes."""
        if not self._running:
            return
        
        try:
            if self.handler:
                self.handler.stop()
                self.handler = None
            
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)  # Wait up to 5 seconds
                self.observer = None
            
            self._running = False
            logger.info("Stopped file watcher")
            
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")
    
    def is_running(self) -> bool:
        """Check if the file watcher is running."""
        return self._running and self.observer is not None and self.observer.is_alive()
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()