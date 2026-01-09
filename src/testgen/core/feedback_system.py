"""
Universal Real-Time Feedback System for TestGen AI.

Provides live status updates during watch mode operations
across ALL 14 programming languages.
"""

from typing import Optional, Callable, List
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import sys


class FeedbackType(str, Enum):
    """Type of feedback message."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"


class FeedbackIcon(str, Enum):
    """Icons for different feedback types."""
    DETECTED = "📝"
    GENERATING = "⚙️"
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠️"
    SPINNER = "🔄"
    FILE = "📄"
    TEST = "🧪"
    LANGUAGE = "🌍"


@dataclass
class FeedbackMessage:
    """A feedback message to display."""
    
    type: FeedbackType
    message: str
    icon: Optional[str] = None
    timestamp: datetime = None
    language: Optional[str] = None
    file_path: Optional[Path] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Auto-assign icon if not provided
        if self.icon is None:
            if self.type == FeedbackType.SUCCESS:
                self.icon = FeedbackIcon.SUCCESS.value
            elif self.type == FeedbackType.ERROR:
                self.icon = FeedbackIcon.ERROR.value
            elif self.type == FeedbackType.WARNING:
                self.icon = FeedbackIcon.WARNING.value
            elif self.type == FeedbackType.PROGRESS:
                self.icon = FeedbackIcon.SPINNER.value
            else:
                self.icon = FeedbackIcon.FILE.value


class UniversalFeedbackSystem:
    """
    Universal real-time feedback system for ALL 14 languages.
    
    Displays status updates during watch mode:
    - File change detection
    - Test generation progress
    - Success/error confirmations
    """
    
    def __init__(
        self,
        show_timestamps: bool = False,
        show_language: bool = True,
        verbose: bool = True
    ):
        """
        Initialize feedback system.
        
        Args:
            show_timestamps: Show timestamps in messages
            show_language: Show language info in messages
            verbose: Show all messages (False = only important)
        """
        self.show_timestamps = show_timestamps
        self.show_language = show_language
        self.verbose = verbose
        
        self.messages: List[FeedbackMessage] = []
        self.callbacks: List[Callable[[FeedbackMessage], None]] = []
        
        # Statistics
        self.changes_detected = 0
        self.tests_generated = 0
        self.errors = 0
    
    def detected_change(
        self,
        file_path: Path,
        language: str,
        is_test_file: bool = False
    ) -> None:
        """
        Show message when file change is detected.
        
        Args:
            file_path: Changed file path
            language: Programming language
            is_test_file: Whether it's a test file
        """
        file_type = "test file" if is_test_file else "source file"
        
        message = f"Detected change in {file_type}: {file_path.name}"
        if self.show_language:
            message = f"{FeedbackIcon.LANGUAGE.value} {language.upper()} - {message}"
        
        self._show_message(
            FeedbackType.INFO,
            message,
            FeedbackIcon.DETECTED.value,
            language=language,
            file_path=file_path
        )
        
        self.changes_detected += 1
    
    def generating_tests(
        self,
        file_path: Path,
        language: str
    ) -> None:
        """
        Show message when test generation starts.
        
        Args:
            file_path: Source file path
            language: Programming language
        """
        message = f"Generating tests for {file_path.name}..."
        if self.show_language:
            message = f"{FeedbackIcon.LANGUAGE.value} {language.upper()} - {message}"
        
        self._show_message(
            FeedbackType.PROGRESS,
            message,
            FeedbackIcon.GENERATING.value,
            language=language,
            file_path=file_path
        )
    
    def tests_updated(
        self,
        test_file: Path,
        language: str,
        duration: Optional[float] = None
    ) -> None:
        """
        Show success message when tests are updated.
        
        Args:
            test_file: Test file path
            language: Programming language
            duration: Generation duration in seconds
        """
        message = f"{FeedbackIcon.SUCCESS.value} Tests updated: {test_file.name}"
        
        if duration is not None:
            message += f" ({duration:.2f}s)"
        
        if self.show_language:
            message = f"{FeedbackIcon.LANGUAGE.value} {language.upper()} - {message}"
        
        self._show_message(
            FeedbackType.SUCCESS,
            message,
            language=language,
            file_path=test_file
        )
        
        self.tests_generated += 1
    
    def skipping_file(
        self,
        file_path: Path,
        reason: str,
        language: Optional[str] = None
    ) -> None:
        """
        Show message when file is skipped.
        
        Args:
            file_path: Skipped file path
            reason: Reason for skipping
            language: Programming language
        """
        message = f"⏩ Skipping {file_path.name}: {reason}"
        
        if language and self.show_language:
            message = f"{FeedbackIcon.LANGUAGE.value} {language.upper()} - {message}"
        
        if self.verbose:
            self._show_message(
                FeedbackType.INFO,
                message,
                language=language,
                file_path=file_path
            )
    
    def error_occurred(
        self,
        message: str,
        file_path: Optional[Path] = None,
        language: Optional[str] = None
    ) -> None:
        """
        Show error message.
        
        Args:
            message: Error message
            file_path: Related file path
            language: Programming language
        """
        error_msg = f"{FeedbackIcon.ERROR.value} Error: {message}"
        
        if language and self.show_language:
            error_msg = f"{FeedbackIcon.LANGUAGE.value} {language.upper()} - {error_msg}"
        
        self._show_message(
            FeedbackType.ERROR,
            error_msg,
            language=language,
            file_path=file_path
        )
        
        self.errors += 1
    
    def watching_started(
        self,
        directories: List[str],
        languages: Optional[List[str]] = None
    ) -> None:
        """
        Show message when watching starts.
        
        Args:
            directories: Directories being watched
            languages: Languages being monitored
        """
        dir_str = ", ".join(directories)
        message = f"👀 Watching {len(directories)} director{'y' if len(directories) == 1 else 'ies'}: {dir_str}"
        
        if languages:
            if len(languages) == 14:
                lang_str = "ALL 14 languages"
            else:
                lang_str = ", ".join(languages)
            message += f"\n   Languages: {lang_str}"
        
        self._show_message(FeedbackType.INFO, message, "🚀")
    
    def watching_stopped(self) -> None:
        """Show message when watching stops."""
        message = f"📴 Watch mode stopped"
        
        if self.changes_detected > 0 or self.tests_generated > 0:
            message += f"\n   Changes detected: {self.changes_detected}"
            message += f"\n   Tests generated: {self.tests_generated}"
            if self.errors > 0:
                message += f"\n   Errors: {self.errors}"
        
        self._show_message(FeedbackType.INFO, message)
    
    def show_statistics(self) -> None:
        """Show current statistics."""
        stats = [
            f"📊 Statistics:",
            f"   Changes detected: {self.changes_detected}",
            f"   Tests generated: {self.tests_generated}",
            f"   Errors: {self.errors}",
        ]
        
        message = "\n".join(stats)
        self._show_message(FeedbackType.INFO, message)
    
    def _show_message(
        self,
        msg_type: FeedbackType,
        message: str,
        icon: Optional[str] = None,
        language: Optional[str] = None,
        file_path: Optional[Path] = None
    ) -> None:
        """
        Internal method to display a message.
        
        Args:
            msg_type: Type of feedback
            message: Message text
            icon: Optional icon
            language: Programming language
            file_path: Related file path
        """
        feedback = FeedbackMessage(
            type=msg_type,
            message=message,
            icon=icon,
            language=language,
            file_path=file_path
        )
        
        self.messages.append(feedback)
        
        # Format message for display
        display_msg = message
        
        if self.show_timestamps:
            timestamp = feedback.timestamp.strftime("%H:%M:%S")
            display_msg = f"[{timestamp}] {display_msg}"
        
        # Print to console
        print(display_msg)
        sys.stdout.flush()
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(feedback)
            except Exception as e:
                print(f"Error in feedback callback: {e}")
    
    def on_feedback(self, callback: Callable[[FeedbackMessage], None]) -> None:
        """
        Register callback for feedback messages.
        
        Args:
            callback: Function to call on each message
        """
        self.callbacks.append(callback)
    
    def get_recent_messages(self, n: int = 10) -> List[FeedbackMessage]:
        """Get recent feedback messages."""
        return self.messages[-n:] if self.messages else []
    
    def clear_messages(self) -> None:
        """Clear message history."""
        self.messages.clear()
    
    def get_statistics(self) -> dict:
        """Get feedback statistics."""
        by_type = {}
        for msg in self.messages:
            msg_type = msg.type.value
            by_type[msg_type] = by_type.get(msg_type, 0) + 1
        
        by_language = {}
        for msg in self.messages:
            if msg.language:
                by_language[msg.language] = by_language.get(msg.language, 0) + 1
        
        return {
            "total_messages": len(self.messages),
            "changes_detected": self.changes_detected,
            "tests_generated": self.tests_generated,
            "errors": self.errors,
            "by_type": by_type,
            "by_language": by_language
        }


# Global feedback instance (convenient for imports)
_global_feedback: Optional[UniversalFeedbackSystem] = None


def get_feedback_system() -> UniversalFeedbackSystem:
    """Get or create global feedback system."""
    global _global_feedback
    if _global_feedback is None:
        _global_feedback = UniversalFeedbackSystem()
    return _global_feedback


def create_feedback_system(
    show_timestamps: bool = False,
    show_language: bool = True,
    verbose: bool = True
) -> UniversalFeedbackSystem:
    """Create a new feedback system instance."""
    return UniversalFeedbackSystem(show_timestamps, show_language, verbose)
