"""
Universal Graceful Shutdown Handler for TestGen AI.

Handles graceful shutdown of watch mode across ALL 14 programming languages.
"""

import signal
import sys
import atexit
from typing import Callable, List, Optional
from datetime import datetime
from pathlib import Path
import json

from .feedback_system import UniversalFeedbackSystem, get_feedback_system
from .watcher import UniversalFileWatcher
from .change_detector import UniversalChangeDetector


class UniversalShutdownHandler:
    """
    Universal graceful shutdown handler for ALL 14 languages.
    
    Handles Ctrl+C (SIGINT), cleans up resources, saves state.
    """
    
    def __init__(
        self,
        feedback_system: Optional[UniversalFeedbackSystem] = None,
        save_state: bool = True,
        state_file: str = ".testgen_state.json"
    ):
        """
        Initialize shutdown handler.
        
        Args:
            feedback_system: Feedback system for messages
            save_state: Whether to save state on shutdown
            state_file: File to save state to
        """
        self.feedback = feedback_system or get_feedback_system()
        self.save_state = save_state
        self.state_file = Path(state_file)
        
        self.shutdown_callbacks: List[Callable[[], None]] = []
        self.watchers: List[UniversalFileWatcher] = []
        self.detectors: List[UniversalChangeDetector] = []
        
        self.is_shutting_down = False
        self._shutdown_initiated_at: Optional[datetime] = None
        
        # Register signal handlers
        self._register_signals()
        
        # Register cleanup on normal exit
        atexit.register(self._cleanup_on_exit)
    
    def _register_signals(self) -> None:
        """Register signal handlers for graceful shutdown."""
        # Handle Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, self._handle_interrupt)
        
        # Handle termination (SIGTERM) if available
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._handle_terminate)
    
    def _handle_interrupt(self, signum, frame) -> None:
        """
        Handle SIGINT (Ctrl+C) signal.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        if self.is_shutting_down:
            # Second Ctrl+C = force quit
            self.feedback._show_message(
                "warning",
                "\n⚠️  Force quitting...",
            )
            sys.exit(1)
        
        self.feedback._show_message(
            "info",
            "\n\n🛑 Shutdown initiated (Ctrl+C detected)...",
        )
        
        self.shutdown()
    
    def _handle_terminate(self, signum, frame) -> None:
        """
        Handle SIGTERM signal.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.feedback._show_message(
            "info",
            "\n🛑 Termination signal received...",
        )
        
        self.shutdown()
    
    def register_watcher(self, watcher: UniversalFileWatcher) -> None:
        """
        Register a watcher for cleanup.
        
        Args:
            watcher: File watcher to clean up
        """
        self.watchers.append(watcher)
    
    def register_detector(self, detector: UniversalChangeDetector) -> None:
        """
        Register a detector for cleanup.
        
        Args:
            detector: Change detector to clean up
        """
        self.detectors.append(detector)
    
    def on_shutdown(self, callback: Callable[[], None]) -> None:
        """
        Register callback to run on shutdown.
        
        Args:
            callback: Function to call on shutdown
        """
        self.shutdown_callbacks.append(callback)
    
    def shutdown(self) -> None:
        """Perform graceful shutdown."""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        self._shutdown_initiated_at = datetime.now()
        
        try:
            # Stop all watchers
            self._stop_watchers()
            
            # Stop all detectors
            self._stop_detectors()
            
            # Run shutdown callbacks
            self._run_callbacks()
            
            # Save state if enabled
            if self.save_state:
                self._save_state()
            
            # Show final statistics
            self._show_final_stats()
            
            self.feedback._show_message(
                "success",
                "✅ Shutdown complete. Goodbye!",
            )
            
        except Exception as e:
            self.feedback._show_message(
                "error",
                f"Error during shutdown: {e}",
            )
        
        finally:
            sys.exit(0)
    
    def _stop_watchers(self) -> None:
        """Stop all registered watchers."""
        if not self.watchers:
            return
        
        self.feedback._show_message(
            "info",
            f"   Stopping {len(self.watchers)} watcher(s)...",
        )
        
        for watcher in self.watchers:
            try:
                if watcher.is_running():
                    watcher.stop()
            except Exception as e:
                print(f"   Error stopping watcher: {e}")
        
        self.watchers.clear()
    
    def _stop_detectors(self) -> None:
        """Stop all registered detectors."""
        if not self.detectors:
            return
        
        self.feedback._show_message(
            "info",
            f"   Stopping {len(self.detectors)} detector(s)...",
        )
        
        for detector in self.detectors:
            try:
                if detector.is_running():
                    detector.stop()
            except Exception as e:
                print(f"   Error stopping detector: {e}")
        
        self.detectors.clear()
    
    def _run_callbacks(self) -> None:
        """Run all shutdown callbacks."""
        if not self.shutdown_callbacks:
            return
        
        self.feedback._show_message(
            "info",
            f"   Running {len(self.shutdown_callbacks)} shutdown callback(s)...",
        )
        
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"   Error in shutdown callback: {e}")
    
    def _save_state(self) -> None:
        """Save current state to file."""
        try:
            state = {
                "shutdown_time": self._shutdown_initiated_at.isoformat() if self._shutdown_initiated_at else None,
                "watchers_stopped": len(self.watchers),
                "detectors_stopped": len(self.detectors),
                "callbacks_run": len(self.shutdown_callbacks),
            }
            
            # Add detector statistics if available
            if self.detectors:
                detector_stats = []
                for detector in self.detectors:
                    try:
                        stats = detector.get_statistics()
                        detector_stats.append(stats)
                    except:
                        pass
                
                if detector_stats:
                    state["detector_stats"] = detector_stats
            
            # Save to file
            self.state_file.write_text(json.dumps(state, indent=2))
            
            self.feedback._show_message(
                "info",
                f"   State saved to {self.state_file}",
            )
            
        except Exception as e:
            print(f"   Error saving state: {e}")
    
    def _show_final_stats(self) -> None:
        """Show final statistics before shutdown."""
        try:
            # Get feedback statistics
            stats = self.feedback.get_statistics()
            
            if stats.get('changes_detected', 0) > 0 or stats.get('tests_generated', 0) > 0:
                self.feedback._show_message(
                    "info",
                    "\n📊 Session Statistics:",
                )
                
                print(f"   Changes detected: {stats.get('changes_detected', 0)}")
                print(f"   Tests generated: {stats.get('tests_generated', 0)}")
                
                if stats.get('errors', 0) > 0:
                    print(f"   Errors: {stats.get('errors', 0)}")
                
                # Show language breakdown if available
                by_lang = stats.get('by_language', {})
                if by_lang:
                    print(f"   Languages: {', '.join(by_lang.keys())}")
        
        except Exception as e:
            print(f"   Error showing stats: {e}")
    
    def _cleanup_on_exit(self) -> None:
        """Cleanup on normal exit (via atexit)."""
        if not self.is_shutting_down:
            # Only run if shutdown wasn't already called
            self.feedback._show_message(
                "info",
                "\n👋 Exiting...",
            )
            
            self._stop_watchers()
            self._stop_detectors()
    
    def load_previous_state(self) -> Optional[dict]:
        """
        Load previous state from file.
        
        Returns:
            Previous state dict or None
        """
        try:
            if self.state_file.exists():
                state_text = self.state_file.read_text()
                return json.loads(state_text)
        except Exception as e:
            print(f"Error loading previous state: {e}")
        
        return None


# Global shutdown handler instance
_global_handler: Optional[UniversalShutdownHandler] = None


def get_shutdown_handler() -> UniversalShutdownHandler:
    """Get or create global shutdown handler."""
    global _global_handler
    if _global_handler is None:
        _global_handler =UniversalShutdownHandler()
    return _global_handler


def create_shutdown_handler(
    feedback_system: Optional[UniversalFeedbackSystem] = None,
    save_state: bool = True
) -> UniversalShutdownHandler:
    """
    Create a new shutdown handler.
    
    Args:
        feedback_system: Feedback system
        save_state: Whether to save state
        
    Returns:
        Shutdown handler instance
    """
    return UniversalShutdownHandler(feedback_system, save_state)


def register_for_shutdown(
    watcher: Optional[UniversalFileWatcher] = None,
    detector: Optional[UniversalChangeDetector] = None,
    callback: Optional[Callable[[], None]] = None
) -> None:
    """
    Convenience function to register components for shutdown.
    
    Args:
        watcher: Watcher to register
        detector: Detector to register
        callback: Callback to register
    """
    handler = get_shutdown_handler()
    
    if watcher:
        handler.register_watcher(watcher)
    
    if detector:
        handler.register_detector(detector)
    
    if callback:
        handler.on_shutdown(callback)
