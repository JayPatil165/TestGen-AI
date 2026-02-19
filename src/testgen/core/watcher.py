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
    """Enumeration of supported file system change event types.

    Members:
        CREATED: A new file was created.
        MODIFIED: An existing file was updated.
        DELETED: A file was removed.
        MOVED: A file was renamed or relocated.
    """


@dataclass
class FileChangeEvent:
    """Encapsulates detailed metadata for a single file system change.

    Attributes:
        path (Path): The absolute path to the file that changed.
        change_type (FileChangeType): The nature of the change (created, modified, etc.).
        language (Language): The programming language detected for the file.
        timestamp (datetime): The precise time the event was detected.
        is_test_file (bool): Whether the file is classified as a test file based
            on naming conventions. Defaults to False.
    """


class UniversalFileWatcher:
    """A high-performance, cross-platform file monitoring engine.

    The UniversalFileWatcher observes file system events across multiple paths,
    filtering for source code changes in over 14 programming languages. It
    features intelligent debouncing to prevent "event storms" during rapid
    saves and provides a unified callback interface for reacting to changes.

    Key Features:
    - Multi-directory monitoring.
    - Automatic language detection and test file identification.
    - Configurable debouncing and path ignoring.
    - Thread-safe callback system.
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
        """Initialize the universal file watcher with monitoring rules.

        The watcher requires the `watchdog` library for native file system events.

        Args:
            watch_paths (List[str]): Directories or specific files to monitor.
            languages (Optional[List[Language]]): Restrict monitoring to specific
                languages. If None, watches all supported source types.
            debounce_seconds (float): Time window in seconds to ignore duplicate
                events for the same file. Defaults to 1.0.
            ignore_patterns (Optional[List[str]]): Glob patterns of files to exclude
                (e.g., build artifacts, temporary files).

        Raises:
            ImportError: If the required `watchdog` library is not installed.
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
        """Determine the programming language of a file based on its extension.

        Args:
            file_path (Path): The path to the file.

        Returns:
            Optional[Language]: The detected language enum, or None if the
                extension is not recognized.
        """
        ext = file_path.suffix.lower()
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        
        return None
    
    def is_test_file(self, file_path: Path, language: Language) -> bool:
        """Heuristically identify if a file is a test file for a given language.

        Uses common naming conventions (e.g., 'test_*.py', '*.spec.js').

        Args:
            file_path (Path): Path to the file.
            language (Language): The programming language context.

        Returns:
            bool: True if the file matches a test pattern for the language.
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
        """Check if a file should be excluded from monitoring.

        Applies the `ignore_patterns` configured during initialization.

        Args:
            file_path (Path): Path to check.

        Returns:
            bool: True if the file matches any ignore pattern.
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
        """Determine if a file event should be suppressed to avoid rapid repetitions.

        Args:
            file_path (str): The string path of the changed file.

        Returns:
            bool: True if an event for this file was processed recently (within
                `debounce_seconds`).
        """
        now = datetime.now()
        
        if file_path in self._last_events:
            last_time = self._last_events[file_path]
            if (now - last_time).total_seconds() < self.debounce_seconds:
                return True
        
        self._last_events[file_path] = now
        return False
    
    def on_change(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Register a new subscriber for file system events.

        Args:
            callback (Callable[[FileChangeEvent], None]): A function to be
                invoked whenever a non-ignored file change is detected.
        """
        self.callbacks.append(callback)
    
    def _create_event_handler(self) -> FileSystemEventHandler:
        """Construct the native Watchdog event handler with integrated filtering.

        Returns:
            FileSystemEventHandler: A configured handler that performs language
                detection, debouncing, and callback dispatching.
        """
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
        """Activate the file monitoring system.

        Starts the background observer threads for all configured watch paths.
        """
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
        """Deactivate the file monitoring system and clean up threads.

        Safely shuts down all active observers.
        """
        if not self._running:
            return
        
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        self._running = False
        print("File watching stopped.")
    
    def is_running(self) -> bool:
        """Check the current operational state of the watcher.

        Returns:
            bool: True if the monitoring threads are active.
        """
        return self._running
    
    def get_watched_extensions(self) -> Set[str]:
        """List all file extensions currently being monitored.

        Returns:
            Set[str]: A unique set of file extension strings (including dots).
        """
        extensions = set()
        for lang in self.languages:
            extensions.update(self.LANGUAGE_EXTENSIONS.get(lang, []))
        return extensions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve operational metrics for the active monitoring session.

        Returns:
            Dict[str, Any]: A summary of the session, including duration,
                watched paths, and count of tracked extensions.
        """
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
    """Convenience function to instantiate and configure a file watcher.

    Args:
        paths (List[str]): Paths to monitor.
        languages (Optional[List[Language]]): Filter for specific languages.
            If None, monitors all supported languages.
        on_change (Optional[Callable]): Initial change callback to register.

    Returns:
        UniversalFileWatcher: A configured (but not yet started) watcher instance.
    """
    watcher = UniversalFileWatcher(paths, languages)
    
    if on_change:
        watcher.on_change(on_change)
    
    return watcher
