"""
Universal File Watcher for TestGen AI.

Monitors file changes across ALL 14 programming languages.
Uses Watchdog library for cross-platform file system events.
"""

from typing import List, Callable, Optional, Set, Dict
from pathlib import Path
import time
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Graceful fallback when watchdog not installed
    Observer = None
    FileSystemEventHandler = object
    FileSystemEvent = object

from .language_config import Language


class FileChangeType(str, Enum):
    """Type of file change event."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileChangeEvent:
    """Represents a file change event."""
    path: Path
    change_type: FileChangeType
    language: Language
    timestamp: datetime
    is_test_file: bool = False


class UniversalFileWatcher:
    """
    Universal file watcher supporting ALL 14 programming languages.
    
    Monitors file changes and triggers callbacks with proper filtering
    and debouncing to avoid rapid repeated events.
    """
    
    # File extensions to watch for each language
    LANGUAGE_EXTENSIONS = {
        Language.PYTHON: ['.py'],
        Language.JAVASCRIPT: ['.js', '.jsx'],
        Language.TYPESCRIPT: ['.ts', '.tsx'],
        Language.JAVA: ['.java'],
        Language.GO: ['.go'],
        Language.CSHARP: ['.cs'],
        Language.RUBY: ['.rb'],
        Language.RUST: ['.rs'],
        Language.PHP: ['.php'],
        Language.SWIFT: ['.swift'],
        Language.KOTLIN: ['.kt', '.kts'],
        Language.CPP: ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
        Language.HTML: ['.html', '.htm'],
        Language.CSS: ['.css', '.scss', '.sass', '.less'],
    }
    
    # Test file patterns for each language
    TEST_PATTERNS = {
        Language.PYTHON: ['test_*.py', '*_test.py', 'tests.py'],
        Language.JAVASCRIPT: ['*.test.js', '*.spec.js', '__tests__/*.js'],
        Language.TYPESCRIPT: ['*.test.ts', '*.spec.ts', '__tests__/*.ts'],
        Language.JAVA: ['*Test.java', 'Test*.java'],
        Language.GO: ['*_test.go'],
        Language.CSHARP: ['*Test.cs', '*Tests.cs'],
        Language.RUBY: ['*_spec.rb', 'spec/*'],
        Language.RUST: ['tests/*.rs', '*_test.rs'],
        Language.PHP: ['*Test.php', 'tests/*'],
        Language.SWIFT: ['*Tests.swift', '*Test.swift'],
        Language.KOTLIN: ['*Test.kt', '*Tests.kt'],
        Language.CPP: ['*_test.cpp', 'test_*.cpp', '*Test.cpp'],
        Language.HTML: [],  # HTML typically tested via other means
        Language.CSS: [],   # CSS typically tested via other means
    }
    
    def __init__(
        self,
        watch_paths: List[str],
        languages: Optional[List[Language]] = None,
        debounce_seconds: float = 1.0,
        ignore_patterns: Optional[List[str]] = None
    ):
        """
        Initialize universal file watcher.
        
        Args:
            watch_paths: List of paths to monitor
            languages: Languages to watch (default: all 14)
            debounce_seconds: Seconds to wait before processing repeated events
            ignore_patterns: Patterns to ignore (e.g., ['*.pyc', '__pycache__'])
        """
        if not WATCHDOG_AVAILABLE:
            raise ImportError(
                "Watchdog library not installed. "
                "Install with: pip install watchdog"
            )
        
        self.watch_paths = [Path(p) for p in watch_paths]
        self.languages = languages or list(self.LANGUAGE_EXTENSIONS.keys())
        self.debounce_seconds = debounce_seconds
        self.ignore_patterns = ignore_patterns or [
            '*.pyc', '__pycache__', '*.pyo', '*.pyd',
            'node_modules', '.git', '.svn', '.hg',
            '*.class', '*.o', '*.obj', '*.so', '*.dll',
            '.idea', '.vscode', '*.swp', '*.swo',
            'build', 'dist', 'target', 'bin', 'obj'
        ]
        
        self.observers: List[Observer] = []
        self.callbacks: List[Callable[[FileChangeEvent], None]] = []
        self._last_events: Dict[str, datetime] = {}
        self._running = False
    
    def detect_language(self, file_path: Path) -> Optional[Language]:
        """
        Detect language from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected language or None
        """
        ext = file_path.suffix.lower()
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        
        return None
    
    def is_test_file(self, file_path: Path, language: Language) -> bool:
        """
        Check if file is a test file based on naming conventions.
        
        Args:
            file_path: Path to file
            language: Programming language
            
        Returns:
            True if test file
        """
        patterns = self.TEST_PATTERNS.get(language, [])
        file_name = file_path.name
        
        for pattern in patterns:
            # Simple pattern matching
            if '*' in pattern:
                prefix, suffix = pattern.split('*', 1)
                if file_name.startswith(prefix) and file_name.endswith(suffix):
                    return True
            elif file_name == pattern:
                return True
        
        # Also check if in tests directory
        return 'test' in str(file_path).lower()
    
    def should_ignore(self, file_path: Path) -> bool:
        """
        Check if file should be ignored based on patterns.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if should be ignored
        """
        path_str = str(file_path)
        
        for pattern in self.ignore_patterns:
            if '*' in pattern:
                # Simple wildcard matching
                pattern_clean = pattern.replace('*', '')
                if pattern_clean in path_str:
                    return True
            elif pattern in path_str:
                return True
        
        return False
    
    def should_debounce(self, file_path: str) -> bool:
        """
        Check if event should be debounced (too soon after last event).
        
        Args:
            file_path: Path that changed
            
        Returns:
            True if should debounce
        """
        now = datetime.now()
        
        if file_path in self._last_events:
            last_time = self._last_events[file_path]
            if (now - last_time).total_seconds() < self.debounce_seconds:
                return True
        
        self._last_events[file_path] = now
        return False
    
    def on_change(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """
        Register callback for file changes.
        
        Args:
            callback: Function to call when files change
        """
        self.callbacks.append(callback)
    
    def _create_event_handler(self):
        """Create event handler for watchdog."""
        watcher = self
        
        class UniversalEventHandler(FileSystemEventHandler):
            """Event handler for file system events."""
            
            def on_any_event(self, event: FileSystemEvent):
                """Handle any file system event."""
                if event.is_directory:
                    return
                
                file_path = Path(event.src_path)
                
                # Ignore unwanted files
                if watcher.should_ignore(file_path):
                    return
                
                # Detect language
                language = watcher.detect_language(file_path)
                if not language or language not in watcher.languages:
                    return
                
                # Debounce rapid changes
                if watcher.should_debounce(str(file_path)):
                    return
                
                # Determine change type
                change_type = FileChangeType.MODIFIED
                if event.event_type == 'created':
                    change_type = FileChangeType.CREATED
                elif event.event_type == 'deleted':
                    change_type = FileChangeType.DELETED
                elif event.event_type == 'moved':
                    change_type = FileChangeType.MOVED
                
                # Check if test file
                is_test = watcher.is_test_file(file_path, language)
                
                # Create event
                change_event = FileChangeEvent(
                    path=file_path,
                    change_type=change_type,
                    language=language,
                    timestamp=datetime.now(),
                    is_test_file=is_test
                )
                
                # Notify callbacks
                for callback in watcher.callbacks:
                    try:
                        callback(change_event)
                    except Exception as e:
                        # Don't let callback errors stop the watcher
                        print(f"Error in callback: {e}")
        
        return UniversalEventHandler()
    
    def start(self) -> None:
        """Start watching for file changes."""
        if self._running:
            return
        
        event_handler = self._create_event_handler()
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                print(f"Warning: Watch path does not exist: {watch_path}")
                continue
            
            observer = Observer()
            observer.schedule(
                event_handler,
                str(watch_path),
                recursive=True
            )
            observer.start()
            self.observers.append(observer)
        
        self._running = True
        print(f"Watching {len(self.watch_paths)} path(s) for changes...")
    
    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self._running:
            return
        
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        self._running = False
        print("File watching stopped.")
    
    def is_running(self) -> bool:
        """Check if watcher is currently running."""
        return self._running
    
    def get_watched_extensions(self) -> Set[str]:
        """Get all file extensions being watched."""
        extensions = set()
        for lang in self.languages:
            extensions.update(self.LANGUAGE_EXTENSIONS.get(lang, []))
        return extensions
    
    def get_statistics(self) -> Dict[str, any]:
        """Get watcher statistics."""
        return {
            "running": self._running,
            "watch_paths": [str(p) for p in self.watch_paths],
            "languages": [lang.value for lang in self.languages],
            "extensions": list(self.get_watched_extensions()),
            "callbacks": len(self.callbacks),
            "observers": len(self.observers),
            "debounce_seconds": self.debounce_seconds
        }


# Convenience function
def create_watcher(
    paths: List[str],
    languages: Optional[List[Language]] = None,
    on_change: Optional[Callable[[FileChangeEvent], None]] = None
) -> UniversalFileWatcher:
    """
    Create and configure a file watcher.
    
    Args:
        paths: Paths to watch
        languages: Languages to watch (default: all 14)
        on_change: Optional callback for changes
        
    Returns:
        Configured watcher
    """
    watcher = UniversalFileWatcher(paths, languages)
    
    if on_change:
        watcher.on_change(on_change)
    
    return watcher
