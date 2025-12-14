"""
Test Generator with Retry Logic and Rate Limiting.

This module handles LLM API calls with robust error handling,
exponential backoff, rate limiting, and timeout management.
"""

import time
import asyncio
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from testgen.core.llm import LLMClient, LLMResponse


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    timeout: float = 120.0  # seconds
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt using exponential backoff."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    requests_per_minute: int = 15  # Gemini free tier
    tokens_per_minute: int = 50000
    
    def __post_init__(self):
        self.requests: list[datetime] = []
        self.tokens: list[tuple[datetime, int]] = []
    
    def can_make_request(self) -> tuple[bool, Optional[float]]:
        """
        Check if request can be made within rate limits.
        
        Returns:
            (can_proceed, wait_time_seconds)
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests = [r for r in self.requests if r > one_minute_ago]
        
        # Check request limit
        if len(self.requests) >= self.requests_per_minute:
            oldest = min(self.requests)
            wait_time = (oldest + timedelta(minutes=1) - now).total_seconds()
            return False, wait_time
        
        return True, None
    
    def record_request(self, tokens: int = 0):
        """Record a request for rate limiting."""
        now = datetime.now()
        self.requests.append(now)
        if tokens > 0:
            self.tokens.append((now, tokens))


class TestGenerator:
    """
    Test generator with robust API handling.
    
    Implements Task 38 requirements:
    - generate_tests() method
    - Exponential backoff
    - Rate limit handling
    - Timeout handling
    
    Example:
        >>> generator = TestGenerator()
        >>> tests = generator.generate_tests("def add(a, b): return a + b")
        >>> print(tests)
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        retry_config: Optional[RetryConfig] = None,
        rate_limit_config: Optional[RateLimitConfig] = None
    ):
        """
        Initialize test generator.
        
        Args:
            llm_client: LLM client to use
            retry_config: Retry configuration
            rate_limit_config: Rate limit configuration
        """
        self.llm_client = llm_client or LLMClient()
        self.retry_config = retry_config or RetryConfig()
        self.rate_limit = rate_limit_config or RateLimitConfig()
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retried_requests = 0
        self.rate_limited_requests = 0
    
    def generate_tests(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate tests with retry logic and rate limiting (Task 38 requirement).
        
        Args:
            prompt: User prompt with code context
            system_prompt: Optional system instruction
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated test code as string
            
        Raises:
            TimeoutError: If generation times out
            RuntimeError: If max retries exceeded
            
        Example:
            >>> generator = TestGenerator()
            >>> code = "def multiply(x, y): return x * y"
            >>> tests = generator.generate_tests(code)
        """
        self.total_requests += 1
        
        # Check rate limits
        can_proceed, wait_time = self.rate_limit.can_make_request()
        if not can_proceed:
            print(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            self.rate_limited_requests += 1
        
        # Try with retries
        for attempt in range(self.retry_config.max_retries):
            try:
                # Make API call with timeout
                response = self._call_with_timeout(
                    prompt,
                    system_prompt,
                    max_tokens,
                    timeout=self.retry_config.timeout
                )
                
                # Record successful request
                self.rate_limit.record_request(response.tokens_used)
                self.successful_requests += 1
                
                return response.content
                
            except TimeoutError as e:
                print(f"Attempt {attempt + 1} timed out: {e}")
                if attempt < self.retry_config.max_retries - 1:
                    delay = self.retry_config.get_delay(attempt)
                    print(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    self.retried_requests += 1
                else:
                    self.failed_requests += 1
                    raise
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                    print(f"Rate limit error on attempt {attempt + 1}: {e}")
                    if attempt < self.retry_config.max_retries - 1:
                        # Use longer delay for rate limits
                        delay = self.retry_config.get_delay(attempt) * 2
                        print(f"Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        self.rate_limited_requests += 1
                        self.retried_requests += 1
                    else:
                        self.failed_requests += 1
                        raise RuntimeError(
                            f"Max retries exceeded. Rate limit error: {e}"
                        ) from e
                
                # Check if it's a temporary error worth retrying
                elif "timeout" in error_msg or "connection" in error_msg or "503" in error_msg:
                    print(f"Temporary error on attempt {attempt + 1}: {e}")
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt)
                        print(f"Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        self.retried_requests += 1
                    else:
                        self.failed_requests += 1
                        raise RuntimeError(
                            f"Max retries exceeded. Last error: {e}"
                        ) from e
                
                # Don't retry permanent errors
                else:
                    print(f"Permanent error: {e}")
                    self.failed_requests += 1
                    raise
        
        # Should never reach here
        self.failed_requests += 1
        raise RuntimeError("Max retries exceeded")
    
    def _call_with_timeout(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        timeout: float
    ) -> LLMResponse:
        """
        Call LLM with timeout handling (Task 38 requirement).
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            max_tokens: Max tokens
            timeout: Timeout in seconds
            
        Returns:
            LLM response
            
        Raises:
            TimeoutError: If call exceeds timeout
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"LLM call exceeded {timeout}s timeout")
        
        # Set up timeout (Unix-like systems)
        # For Windows, we'll use a simple approach
        try:
            # Try to use signal (works on Unix)
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))
        except (AttributeError, ValueError):
            # Windows doesn't support SIGALRM
            # We'll rely on LiteLLM's internal timeout
            pass
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )
            return response
        finally:
            try:
                signal.alarm(0)  # Cancel alarm
                signal.signal(signal.SIGALRM, old_handler)
            except (AttributeError, ValueError):
                pass
    
    async def generate_tests_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> str:
        """
        Async version of generate_tests with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            max_tokens: Max tokens
            
        Returns:
            Generated test code
        """
        self.total_requests += 1
        
        # Check rate limits
        can_proceed, wait_time = self.rate_limit.can_make_request()
        if not can_proceed:
            print(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
            self.rate_limited_requests += 1
        
        # Try with retries
        for attempt in range(self.retry_config.max_retries):
            try:
                # Make async API call
                response = await self.llm_client.generate_async(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens
                )
                
                # Record successful request
                self.rate_limit.record_request(response.tokens_used)
                self.successful_requests += 1
                
                return response.content
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle rate limiting
                if "rate" in error_msg or "quota" in error_msg:
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt) * 2
                        print(f"Rate limited. Waiting {delay:.1f}s...")
                        await asyncio.sleep(delay)
                        self.rate_limited_requests += 1
                        self.retried_requests += 1
                    else:
                        self.failed_requests += 1
                        raise
                
                # Handle temporary errors
                elif "timeout" in error_msg or "connection" in error_msg:
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt)
                        await asyncio.sleep(delay)
                        self.retried_requests += 1
                    else:
                        self.failed_requests += 1
                        raise
                
                # Don't retry permanent errors
                else:
                    self.failed_requests += 1
                    raise
        
        self.failed_requests += 1
        raise RuntimeError("Max retries exceeded")
    
    def get_statistics(self) -> dict:
        """
        Get statistics about API calls.
        
        Returns:
            Dictionary with statistics
        """
        success_rate = (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0
            else 0
        )
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "retried_requests": self.retried_requests,
            "rate_limited_requests": self.rate_limited_requests,
            "success_rate": f"{success_rate:.1f}%"
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retried_requests = 0
        self.rate_limited_requests = 0
