"""
Universal File Change Detector for TestGen AI.

Implements smart file change detection for ALL 14 programming languages
with filtering, debouncing, and language-aware monitoring.
"""

from typing import List, Optional, Callable, Dict, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .watcher import (
    UniversalFileWatcher,
    FileChangeEvent,
    FileChangeType,
    WATCHDOG_AVAILABLE
)
from .language_config import Language


class ChangeFilter(str, Enum):
    """Filter modes for change detection."""
    ALL = "all"                    # All file changes
    SAVE_ONLY = "save_only"        # Only saved files (modified)
    SOURCE_ONLY = "source_only"    # Only source code files (not tests)
    TEST_ONLY = "test_only"        # Only test files
    LANGUAGE = "language"          # Specific language(s)


@dataclass
class ChangeDetectionConfig:
    """Configuration for change detection."""
    
    # Directories to monitor
    watch_directories: List[str] = field(default_factory=list)
    
    # Languages to monitor (default: all 14)
    languages: Optional[List[Language]] = None
    
    # Filter mode
    filter_mode: ChangeFilter = ChangeFilter.SAVE_ONLY
    
    # Debounce time (seconds)
    debounce_seconds: float = 1.0
    
    # Include subdirectories
    recursive: bool = True
    
    # Custom ignore patterns (in addition to defaults)
    ignore_patterns: List[str] = field(default_factory=list)
    
    # Only trigger on test files
    test_files_only: bool = False
    
    # Only trigger on source files (exclude tests)
    source_files_only: bool = False
    
    # Minimum file size to trigger (bytes, 0 = no limit)
    min_file_size: int = 0
    
    # Maximum file size to trigger (bytes, 0 = no limit)
    max_file_size: int = 0


@dataclass
class DetectedChange:
    """Represents a detected and filtered file change."""
    
    event: FileChangeEvent
    detection_time: datetime
    source_file: Path
    is_test_file: bool
    language: Language
    should_trigger_generation: bool = True
    
    def __str__(self) -> str:
        change_type = self.event.change_type.value.upper()
        file_type = "TEST" if self.is_test_file else "SOURCE"
        return f"{change_type} {file_type}: {self.source_file.name} ({self.language.value})"


class UniversalChangeDetector:
    """
    Universal file change detector supporting ALL 14 programming languages.
    
    Provides smart filtering, debouncing, and language-aware change detection
    for automated test generation triggering.
    """
    
    def __init__(self, config: Optional[ChangeDetectionConfig] = None):
        """
        Initialize change detector.
        
        Args:
            config: Configuration for change detection
        """
        self.config = config or ChangeDetectionConfig()
        
        if not self.config.watch_directories:
            self.config.watch_directories = ["."]
        
        self.watcher: Optional[UniversalFileWatcher] = None
        self.detected_changes: List[DetectedChange] = []
        self.change_callbacks: List[Callable[[DetectedChange], None]] = []
        self._is_running = False
        
        # Statistics
        self.total_events = 0
        self.filtered_events = 0
        self.triggered_events = 0
    
    def _should_process_change(self, event: FileChangeEvent) -> bool:
        """
        Determine if a change event should be processed.
        
        Args:
            event: File change event
            
        Returns:
            True if should process
        """
        # Filter by change type (save only)
        if self.config.filter_mode == ChangeFilter.SAVE_ONLY:
            if event.change_type not in [FileChangeType.MODIFIED, FileChangeType.CREATED]:
                return False
        
        # Filter by test/source
        if self.config.test_files_only and not event.is_test_file:
            return False
        
        if self.config.source_files_only and event.is_test_file:
            return False
        
        # Filter by file size
        if event.path.exists():
            file_size = event.path.stat().st_size
            
            if self.config.min_file_size > 0 and file_size < self.config.min_file_size:
                return False
            
            if self.config.max_file_size > 0 and file_size > self.config.max_file_size:
                return False
        
        return True
    
    def _create_detected_change(self, event: FileChangeEvent) -> DetectedChange:
        """
        Create a DetectedChange from event.
        
        Args:
            event: File change event
            
        Returns:
            DetectedChange object
        """
        return DetectedChange(
            event=event,
            detection_time=datetime.now(),
            source_file=event.path,
            is_test_file=event.is_test_file,
            language=event.language,
            should_trigger_generation=not event.is_test_file  # Generate tests for source, not for tests
        )
    
    def _on_file_change(self, event: FileChangeEvent) -> None:
        """
        Handle file change event from watcher.
        
        Args:
            event: File change event
        """
        self.total_events += 1
        
        # Apply filters
        if not self._should_process_change(event):
            self.filtered_events += 1
            return
        
        # Create detected change
        detected_change = self._create_detected_change(event)
        self.detected_changes.append(detected_change)
        self.triggered_events += 1
        
        # Notify callbacks
        for callback in self.change_callbacks:
            try:
                callback(detected_change)
            except Exception as e:
                print(f"Error in change callback: {e}")
    
    def on_change(self, callback: Callable[[DetectedChange], None]) -> None:
        """
        Register callback for detected changes.
        
        Args:
            callback: Function to call when changes are detected
        """
        self.change_callbacks.append(callback)
    
    def start(self) -> None:
        """Start monitoring for file changes."""
        if self._is_running:
            print("Change detector already running")
            return
        
        if not WATCHDOG_AVAILABLE:
            raise ImportError("Watchdog library required. Install: pip install watchdog")
        
        # Create watcher
        self.watcher = UniversalFileWatcher(
            watch_paths=self.config.watch_directories,
            languages=self.config.languages,
            debounce_seconds=self.config.debounce_seconds,
            ignore_patterns=self.config.ignore_patterns
        )
        
        # Register our change handler
        self.watcher.on_change(self._on_file_change)
        
        # Start watching
        self.watcher.start()
        self._is_running = True
        
        print(f"📡 Change detector started monitoring {len(self.config.watch_directories)} directory(ies)")
        print(f"   Languages: {len(self.config.languages or []) or 'ALL 14'}")
        print(f"   Filter: {self.config.filter_mode.value}")
        print(f"   Debounce: {self.config.debounce_seconds}s")
    
    def stop(self) -> None:
        """Stop monitoring for file changes."""
        if not self._is_running:
            return
        
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
        
        self._is_running = False
        print("📴 Change detector stopped")
    
    def is_running(self) -> bool:
        """Check if detector is running."""
        return self._is_running
    
    def get_detected_changes(
        self,
        language: Optional[Language] = None,
        test_files_only: bool = False,
        source_files_only: bool = False
    ) -> List[DetectedChange]:
        """
        Get list of detected changes with optional filtering.
        
        Args:
            language: Filter by language
            test_files_only: Only test files
            source_files_only: Only source files
            
        Returns:
            List of detected changes
        """
        changes = self.detected_changes
        
        if language:
            changes = [c for c in changes if c.language == language]
        
        if test_files_only:
            changes = [c for c in changes if c.is_test_file]
        
        if source_files_only:
            changes = [c for c in changes if not c.is_test_file]
        
        return changes
    
    def get_changes_requiring_generation(self) -> List[DetectedChange]:
        """
        Get changes that should trigger test generation.
        
        Returns:
            List of changes requiring generation
        """
        return [c for c in self.detected_changes if c.should_trigger_generation]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get detector statistics.
        
        Returns:
            Statistics dictionary
        """
        changes_by_language = {}
        for change in self.detected_changes:
            lang = change.language.value
            changes_by_language[lang] = changes_by_language.get(lang, 0) + 1
        
        return {
            "running": self._is_running,
            "total_events": self.total_events,
            "filtered_events": self.filtered_events,
            "triggered_events": self.triggered_events,
            "detected_changes": len(self.detected_changes),
            "changes_by_language": changes_by_language,
            "filter_mode": self.config.filter_mode.value,
            "debounce_seconds": self.config.debounce_seconds,
            "watch_directories": self.config.watch_directories,
            "test_files_detected": sum(1 for c in self.detected_changes if c.is_test_file),
            "source_files_detected": sum(1 for c in self.detected_changes if not c.is_test_file),
        }
    
    def clear_changes(self) -> None:
        """Clear detected changes history."""
        self.detected_changes.clear()
    
    def get_latest_change(self) -> Optional[DetectedChange]:
        """Get most recent detected change."""
        return self.detected_changes[-1] if self.detected_changes else None
    
    def get_changes_since(self, since: datetime) -> List[DetectedChange]:
        """
        Get changes detected since a specific time.
        
        Args:
            since: Datetime to filter from
            
        Returns:
            List of changes since the time
        """
        return [c for c in self.detected_changes if c.detection_time >= since]
    
    def get_unique_files_changed(self) -> Set[Path]:
        """Get set of unique files that have changed."""
        return {c.source_file for c in self.detected_changes}
    
    def get_changes_by_language(self, language: Language) -> List[DetectedChange]:
        """Get all changes for a specific language."""
        return [c for c in self.detected_changes if c.language == language]


# Convenience functions

def create_detector(
    directories: List[str],
    languages: Optional[List[Language]] = None,
    save_only: bool = True,
    debounce_seconds: float = 1.0,
    on_change: Optional[Callable[[DetectedChange], None]] = None
) -> UniversalChangeDetector:
    """
    Create a configured change detector.
    
    Args:
        directories: Directories to monitor
        languages: Languages to watch (default: all)
        save_only: Only trigger on saves (not deletes)
        debounce_seconds: Debounce time
        on_change: Optional callback
        
    Returns:
        Configured detector
    """
    config = ChangeDetectionConfig(
        watch_directories=directories,
        languages=languages,
        filter_mode=ChangeFilter.SAVE_ONLY if save_only else ChangeFilter.ALL,
        debounce_seconds=debounce_seconds
    )
    
    detector = UniversalChangeDetector(config)
    
    if on_change:
        detector.on_change(on_change)
    
    return detector


def create_test_only_detector(
    directories: List[str],
    languages: Optional[List[Language]] = None
) -> UniversalChangeDetector:
    """
    Create detector that only watches test files.
    
    Args:
        directories: Directories to monitor
        languages: Languages to watch
        
    Returns:
        Test-only detector
    """
    config = ChangeDetectionConfig(
        watch_directories=directories,
        languages=languages,
        test_files_only=True
    )
    
    return UniversalChangeDetector(config)


def create_source_only_detector(
    directories: List[str],
    languages: Optional[List[Language]] = None
) -> UniversalChangeDetector:
    """
    Create detector that only watches source files (not tests).
    
    Args:
        directories: Directories to monitor
        languages: Languages to watch
        
    Returns:
        Source-only detector
    """
    config = ChangeDetectionConfig(
        watch_directories=directories,
        languages=languages,
        source_files_only=True
    )
    
    return UniversalChangeDetector(config)
