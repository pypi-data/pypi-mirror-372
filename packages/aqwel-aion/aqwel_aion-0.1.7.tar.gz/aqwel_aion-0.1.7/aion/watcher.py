#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 File Watcher Module
=====================================

Real-time file monitoring and change detection for AI research projects.
Enhanced in v0.1.7 with improved monitoring capabilities and event handling.

Features:
- Real-time file change monitoring and detection
- Multiple file watching with individual callbacks
- Thread-safe monitoring operations
- Configurable polling intervals
- Event-driven file change notifications
- Automatic cleanup and resource management

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from datetime import datetime

class FileWatcher:
    """Enhanced file watcher with real-time monitoring."""
    
    def __init__(self):
        self.watched_files = {}
        self.running = False
        self.thread = None
    
    def watch_file_for_changes(self, filepath: str, callback: Callable[[str], None], 
                              interval: float = 1.0) -> bool:
        """Watch a file for changes and call callback when modified."""
        if not os.path.exists(filepath):
            print(f"Warning: File {filepath} does not exist")
            return False
        
        self.watched_files[filepath] = {
            'callback': callback,
            'last_modified': os.path.getmtime(filepath),
            'interval': interval
        }
        
        if not self.running:
            self.start_watching()
        
        return True
    
    def start_watching(self):
        """Start the file watching thread."""
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
    
    def stop_watching(self):
        """Stop the file watching thread."""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _watch_loop(self):
        """Main watching loop."""
        while self.running:
            for filepath, info in self.watched_files.items():
                try:
                    if os.path.exists(filepath):
                        current_mtime = os.path.getmtime(filepath)
                        if current_mtime > info['last_modified']:
                            info['last_modified'] = current_mtime
                            info['callback'](filepath)
                except Exception as e:
                    print(f"Error watching {filepath}: {e}")
            
            time.sleep(min(info['interval'] for info in self.watched_files.values()) if self.watched_files else 1.0)
    
    def unwatch_file(self, filepath: str) -> bool:
        """Stop watching a specific file."""
        if filepath in self.watched_files:
            del self.watched_files[filepath]
            return True
        return False
    
    def get_watched_files(self) -> list:
        """Get list of currently watched files."""
        return list(self.watched_files.keys())

# Global watcher instance
_watcher = FileWatcher()

def watch_file_for_changes(filepath: str, callback: Callable[[str], None], 
                          interval: float = 1.0) -> bool:
    """Watch a file for changes and call callback when modified."""
    return _watcher.watch_file_for_changes(filepath, callback, interval)

def unwatch_file(filepath: str) -> bool:
    """Stop watching a specific file."""
    return _watcher.unwatch_file(filepath)

def get_watched_files() -> list:
    """Get list of currently watched files."""
    return _watcher.get_watched_files()

def stop_all_watchers():
    """Stop all file watchers."""
    _watcher.stop_watching()

class DirectoryWatcher:
    """Watch entire directories for changes."""
    
    def __init__(self, directory: str, callback: Callable[[str, str], None], 
                 file_pattern: str = "*"):
        self.directory = directory
        self.callback = callback
        self.file_pattern = file_pattern
        self.running = False
        self.thread = None
        self.file_states = {}
    
    def start(self):
        """Start watching the directory."""
        self.running = True
        self.thread = threading.Thread(target=self._watch_directory, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop watching the directory."""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _watch_directory(self):
        """Watch directory for file changes."""
        while self.running:
            try:
                current_files = set()
                for file_path in Path(self.directory).glob(self.file_pattern):
                    if file_path.is_file():
                        current_files.add(str(file_path))
                        current_mtime = file_path.stat().st_mtime
                        
                        if str(file_path) not in self.file_states:
                            # New file
                            self.file_states[str(file_path)] = current_mtime
                            self.callback(str(file_path), "created")
                        elif current_mtime > self.file_states[str(file_path)]:
                            # Modified file
                            self.file_states[str(file_path)] = current_mtime
                            self.callback(str(file_path), "modified")
                
                # Check for deleted files
                deleted_files = set(self.file_states.keys()) - current_files
                for deleted_file in deleted_files:
                    del self.file_states[deleted_file]
                    self.callback(deleted_file, "deleted")
                
                time.sleep(1.0)
            except Exception as e:
                print(f"Error watching directory {self.directory}: {e}")
                time.sleep(5.0)

def watch_directory(directory: str, callback: Callable[[str, str], None], 
                   file_pattern: str = "*") -> DirectoryWatcher:
    """Watch a directory for file changes."""
    watcher = DirectoryWatcher(directory, callback, file_pattern)
    watcher.start()
    return watcher

class CodeWatcher:
    """Specialized watcher for code files with language detection."""
    
    def __init__(self, filepath: str, on_change: Callable[[str, Dict], None]):
        self.filepath = filepath
        self.on_change = on_change
        self.last_content = ""
        self.last_analysis = {}
    
    def start(self):
        """Start watching the code file."""
        watch_file_for_changes(self.filepath, self._handle_change)
    
    def _handle_change(self, filepath: str):
        """Handle file changes with code analysis."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content != self.last_content:
                self.last_content = content
                
                # Import here to avoid circular imports
                from .parser import detect_language, parse_code
                
                language = detect_language(content)
                analysis = parse_code(content, language)
                
                self.last_analysis = analysis
                self.on_change(filepath, analysis)
                
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")

def watch_code_file(filepath: str, on_change: Callable[[str, Dict], None]) -> CodeWatcher:
    """Watch a code file with automatic language detection and analysis."""
    watcher = CodeWatcher(filepath, on_change)
    watcher.start()
    return watcher

def create_file_monitor(filepath: str, callback: Callable[[str, Dict], None]) -> Dict[str, Any]:
    """Create a comprehensive file monitor with metadata."""
    if not os.path.exists(filepath):
        return {"error": "File does not exist"}
    
    try:
        stat = os.stat(filepath)
        monitor_info = {
            "filepath": filepath,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "watcher": watch_code_file(filepath, callback)
        }
        return monitor_info
    except Exception as e:
        return {"error": str(e)}

def get_file_change_history(filepath: str, max_entries: int = 10) -> list:
    """Get recent change history for a file (simulated)."""
    # This would typically read from a log or database
    # For now, return a simulated history
    return [
        {"timestamp": datetime.now(), "action": "modified", "size": os.path.getsize(filepath) if os.path.exists(filepath) else 0}
        for _ in range(max_entries)
    ]