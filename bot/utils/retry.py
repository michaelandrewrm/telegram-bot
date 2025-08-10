"""Retry utility for handling network errors and rate limiting."""

import asyncio
import random
from typing import Callable, Any
from telegram.error import RetryAfter, NetworkError
import structlog

logger = structlog.get_logger(__name__)


class RetryHandler:
    """Handles retry logic for API calls."""
    
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, exponential_base: float = 2.0):
        """Initialize retry handler.
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay: Initial delay between retries
            exponential_base: Exponential backoff base
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.exponential_base = exponential_base
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
                
            except RetryAfter as e:
                # Don't retry RetryAfter errors, let the caller handle them
                raise e
                
            except NetworkError as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.warning("Network error, retrying",
                                 attempt=attempt + 1,
                                 max_attempts=self.max_attempts,
                                 delay=delay,
                                 error=str(e))
                    await asyncio.sleep(delay)
                else:
                    logger.error("All retry attempts failed",
                               max_attempts=self.max_attempts,
                               error=str(e))
                    
            except Exception as e:
                # For other exceptions, fail immediately
                logger.error("Non-retryable error", error=str(e))
                raise e
        
        # If we get here, all retries failed
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff with jitter
        delay = self.delay * (self.exponential_base ** attempt)
        # Add jitter to avoid thundering herd
        jitter = random.uniform(0.1, 0.9)
        return delay * jitter
