"""
Universal Rate Limiter for TestGen AI.

Limits LLM API calls during watch mode to prevent overwhelming the API
across ALL 14 programming languages.
"""

import time
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from queue import Queue, Empty
from threading import Lock

from .feedback_system import UniversalFeedbackSystem, get_feedback_system
from .change_detector import DetectedChange


@dataclass
class QueuedRequest:
    """A queued LLM request."""
    
    change: DetectedChange
    timestamp: datetime
    priority: int = 0  # Higher = more important
    
    def __post_init__(self):
        if not hasattr(self, 'timestamp') or self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    # Maximum requests per minute
    max_requests_per_minute: int = 10
    
    # Batch delay (seconds) - wait this long to batch changes
    batch_delay: float = 2.0
    
    # Maximum batch size
    max_batch_size: int = 5
    
    # Minimum delay between requests (seconds)
    min_request_delay: float = 1.0


class UniversalRateLimiter:
    """
    Universal rate limiter for ALL 14 programming languages.
    
    Queues changes, batches requests, and enforces rate limits
    to prevent overwhelming the LLM API.
    """
    
    def __init__(
        self,
        config: Optional[RateLimitConfig] = None,
        feedback_system: Optional[UniversalFeedbackSystem] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
            feedback_system: Feedback system for messages
        """
        self.config = config or RateLimitConfig()
        self.feedback = feedback_system or get_feedback_system()
        
        self.request_queue: Queue[QueuedRequest] = Queue()
        self.processing_callbacks: List[Callable[[List[DetectedChange]], None]] = []
        
        self._lock = Lock()
        self._request_times: List[datetime] = []
        self._last_request_time: Optional[datetime] = None
        self._pending_batch: List[QueuedRequest] = []
        self._batch_timer_start: Optional[datetime] = None
        
        # Statistics
        self.total_queued = 0
        self.total_processed = 0
        self.total_batched = 0
        self.requests_rate_limited = 0
    
    def queue_change(self, change: DetectedChange, priority: int = 0) -> None:
        """
        Queue a change for processing with rate limiting.
        
        Args:
            change: Detected file change
            priority: Priority (higher = process sooner)
        """
        request = QueuedRequest(
            change=change,
            timestamp=datetime.now(),
            priority=priority
        )
        
        self.request_queue.put(request)
        self.total_queued += 1
        
        if self.feedback.verbose:
            self.feedback._show_message(
                "info",
                f"⏳ Queued: {change.source_file.name} (queue size: {self.request_queue.qsize()})",
                language=change.language.value
            )
    
    def can_make_request(self) -> bool:
        """
        Check if we can make a request now based on rate limits.
        
        Returns:
            True if request is allowed
        """
        now = datetime.now()
        
        # Check minimum delay since last request
        if self._last_request_time:
            elapsed = (now - self._last_request_time).total_seconds()
            if elapsed < self.config.min_request_delay:
                return False
        
        # Check requests per minute limit
        cutoff = now - timedelta(minutes=1)
        
        with self._lock:
            # Remove old request times
            self._request_times = [t for t in self._request_times if t > cutoff]
            
            # Check if under limit
            if len(self._request_times) >= self.config.max_requests_per_minute:
                return False
        
        return True
    
    def record_request(self) -> None:
        """Record that a request was made."""
        now = datetime.now()
        
        with self._lock:
            self._request_times.append(now)
            self._last_request_time = now
    
    def should_process_batch(self) -> bool:
        """
        Check if batch should be processed.
        
        Returns:
            True if batch should be processed now
        """
        if not self._pending_batch:
            return False
        
        # Process if batch is full
        if len(self._pending_batch) >= self.config.max_batch_size:
            return True
        
        # Process if batch delay elapsed
        if self._batch_timer_start:
            elapsed = (datetime.now() - self._batch_timer_start).total_seconds()
            if elapsed >= self.config.batch_delay:
                return True
        
        return False
    
    def add_to_batch(self, request: QueuedRequest) -> None:
        """
        Add request to pending batch.
        
        Args:
            request: Queued request
        """
        if not self._pending_batch:
            self._batch_timer_start = datetime.now()
        
        self._pending_batch.append(request)
        
        if self.feedback.verbose:
            self.feedback._show_message(
                "info",
                f"📦 Batching: {request.change.source_file.name} ({len(self._pending_batch)}/{self.config.max_batch_size})",
                language=request.change.language.value
            )
    
    def process_batch(self) -> None:
        """Process the pending batch."""
        if not self._pending_batch:
            return
        
        # Sort by priority
        self._pending_batch.sort(key=lambda r: r.priority, reverse=True)
        
        # Extract changes
        changes = [req.change for req in self._pending_batch]
        
        # Show feedback
        if len(changes) > 1:
            self.feedback._show_message(
                "info",
                f"🔄 Processing batch of {len(changes)} changes...",
            )
            self.total_batched += 1
        
        # Notify callbacks
        for callback in self.processing_callbacks:
            try:
                callback(changes)
            except Exception as e:
                self.feedback.error_occurred(f"Batch processing error: {e}")
        
        self.total_processed += len(changes)
        
        # Record request
        self.record_request()
        
        # Clear batch
        self._pending_batch.clear()
        self._batch_timer_start = None
    
    def process_queue(self) -> None:
        """
        Process queued requests with rate limiting.
        
        Call this periodically to process the queue.
        """
        # Process any pending batch
        if self.should_process_batch():
            if self.can_make_request():
                self.process_batch()
            else:
                self.requests_rate_limited += 1
                if self.feedback.verbose:
                    self.feedback._show_message(
                        "warning",
                        "⏸️  Rate limit reached, waiting...",
                    )
                return
        
        # Try to get new requests
        while not self.request_queue.empty():
            try:
                request = self.request_queue.get_nowait()
                
                # Add to batch
                self.add_to_batch(request)
                
                # Process if batch is ready and we can make request
                if self.should_process_batch() and self.can_make_request():
                    self.process_batch()
                    
            except Empty:
                break
    
    def on_batch_ready(self, callback: Callable[[List[DetectedChange]], None]) -> None:
        """
        Register callback for when batch is ready to process.
        
        Args:
            callback: Function to call with batched changes
        """
        self.processing_callbacks.append(callback)
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self.request_queue.qsize()
    
    def get_batch_size(self) -> int:
        """Get current batch size."""
        return len(self._pending_batch)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        with self._lock:
            recent_requests = len([t for t in self._request_times if t > cutoff])
        
        return {
            "queue_size": self.get_queue_size(),
            "batch_size": self.get_batch_size(),
            "total_queued": self.total_queued,
            "total_processed": self.total_processed,
            "total_batched": self.total_batched,
            "requests_rate_limited": self.requests_rate_limited,
            "requests_last_minute": recent_requests,
            "max_requests_per_minute": self.config.max_requests_per_minute,
            "batch_delay": self.config.batch_delay,
            "min_request_delay": self.config.min_request_delay
        }
    
    def wait_if_needed(self) -> float:
        """
        Wait if rate limit requires it.
        
        Returns:
            Seconds waited
        """
        if not self._last_request_time:
            return 0.0
        
        now = datetime.now()
        elapsed = (now - self._last_request_time).total_seconds()
        
        if elapsed < self.config.min_request_delay:
            wait_time = self.config.min_request_delay - elapsed
            time.sleep(wait_time)
            return wait_time
        
        return 0.0


# Convenience functions

def create_rate_limiter(
    max_requests_per_minute: int = 10,
    batch_delay: float = 2.0,
    feedback_system: Optional[UniversalFeedbackSystem] = None
) -> UniversalRateLimiter:
    """
    Create a rate limiter with custom settings.
    
    Args:
        max_requests_per_minute: Max LLM requests per minute
        batch_delay: Seconds to wait before batching
        feedback_system: Feedback system
        
    Returns:
        Configured rate limiter
    """
    config = RateLimitConfig(
        max_requests_per_minute=max_requests_per_minute,
        batch_delay=batch_delay
    )
    
    return UniversalRateLimiter(config, feedback_system)
