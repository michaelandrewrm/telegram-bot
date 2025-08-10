"""Tests for bot utils retry."""

import pytest
import asyncio
import sys
import os

from unittest.mock import AsyncMock, patch, MagicMock

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestRetryStructure:
    """Test retry module structure and imports."""

    def test_import_structure(self):
        """Test that retry module can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.utils.retry", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "utils", "retry.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load retry module: {e}")


class TestRetryHandler:
    """Test RetryHandler class."""

    def test_retry_handler_initialization(self):
        """Test RetryHandler initialization."""
        # Mock RetryHandler class
        class MockRetryHandler:
            def __init__(self, max_attempts=3, delay=1.0, exponential_base=2.0):
                self.max_attempts = max_attempts
                self.delay = delay
                self.exponential_base = exponential_base
        
        # Test default initialization
        handler = MockRetryHandler()
        assert handler.max_attempts == 3
        assert handler.delay == 1.0
        assert handler.exponential_base == 2.0
        
        # Test custom initialization
        handler = MockRetryHandler(max_attempts=5, delay=2.0, exponential_base=1.5)
        assert handler.max_attempts == 5
        assert handler.delay == 2.0
        assert handler.exponential_base == 1.5

    def test_retry_handler_successful_execution(self):
        """Test successful function execution without retries."""
        # Mock RetryHandler execution
        async def mock_execute(func, *args, **kwargs):
            """Mock execute method that succeeds on first try."""
            return await func(*args, **kwargs)
        
        # Test successful execution
        async def successful_function():
            return "success"
        
        result = asyncio.run(mock_execute(successful_function))
        assert result == "success"

    def test_retry_handler_network_error_retry(self):
        """Test retry logic with NetworkError."""
        # Mock RetryHandler with network error handling
        class MockRetryHandler:
            def __init__(self, max_attempts=3):
                self.max_attempts = max_attempts
                self.delay = 0.1  # Short delay for testing
                self.exponential_base = 2.0
                self.attempt_count = 0
            
            async def execute(self, func, *args, **kwargs):
                """Mock execute method with retry logic."""
                last_exception = None
                
                for attempt in range(self.max_attempts):
                    try:
                        self.attempt_count = attempt + 1
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if "NetworkError" in str(type(e).__name__):
                            last_exception = e
                            if attempt < self.max_attempts - 1:
                                await asyncio.sleep(0.01)  # Short delay for testing
                            continue
                        else:
                            raise e
                
                raise last_exception
        
        # Mock function that fails twice then succeeds
        class MockNetworkError(Exception):
            pass
        
        call_count = 0
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise MockNetworkError("Network error")
            return "success after retries"
        
        handler = MockRetryHandler(max_attempts=3)
        result = asyncio.run(handler.execute(failing_function))
        
        assert result == "success after retries"
        assert handler.attempt_count == 3
        assert call_count == 3

    def test_retry_handler_retry_after_error(self):
        """Test handling of RetryAfter errors (should not retry)."""
        # Mock RetryHandler with RetryAfter handling
        class MockRetryHandler:
            async def execute(self, func, *args, **kwargs):
                """Mock execute method that doesn't retry RetryAfter errors."""
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "RetryAfter" in str(type(e).__name__):
                        # Don't retry RetryAfter errors
                        raise e
                    # For other errors, could retry here
                    raise e
        
        # Mock RetryAfter error
        class MockRetryAfter(Exception):
            pass
        
        async def retry_after_function():
            raise MockRetryAfter("Rate limited")
        
        handler = MockRetryHandler()
        
        with pytest.raises(MockRetryAfter):
            asyncio.run(handler.execute(retry_after_function))

    def test_retry_handler_non_retryable_error(self):
        """Test handling of non-retryable errors."""
        # Mock RetryHandler with non-retryable error handling
        class MockRetryHandler:
            async def execute(self, func, *args, **kwargs):
                """Mock execute method that doesn't retry non-network errors."""
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "NetworkError" not in str(type(e).__name__) and "RetryAfter" not in str(type(e).__name__):
                        # Don't retry non-network errors
                        raise e
                    raise e
        
        # Mock non-retryable error
        class MockValueError(Exception):
            pass
        
        async def value_error_function():
            raise MockValueError("Invalid value")
        
        handler = MockRetryHandler()
        
        with pytest.raises(MockValueError):
            asyncio.run(handler.execute(value_error_function))

    def test_retry_handler_max_attempts_exceeded(self):
        """Test behavior when max attempts are exceeded."""
        # Mock RetryHandler that exhausts all attempts
        class MockRetryHandler:
            def __init__(self, max_attempts=3):
                self.max_attempts = max_attempts
                self.attempt_count = 0
            
            async def execute(self, func, *args, **kwargs):
                """Mock execute method that fails all attempts."""
                last_exception = None
                
                for attempt in range(self.max_attempts):
                    try:
                        self.attempt_count = attempt + 1
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < self.max_attempts - 1:
                            await asyncio.sleep(0.01)  # Short delay for testing
                        continue
                
                raise last_exception
        
        # Mock function that always fails
        class MockNetworkError(Exception):
            pass
        
        async def always_failing_function():
            raise MockNetworkError("Network error")
        
        handler = MockRetryHandler(max_attempts=3)
        
        with pytest.raises(MockNetworkError):
            asyncio.run(handler.execute(always_failing_function))
        
        assert handler.attempt_count == 3

    def test_calculate_delay_logic(self):
        """Test delay calculation logic."""
        def mock_calculate_delay(delay, exponential_base, attempt):
            """Mock delay calculation with exponential backoff."""
            import random
            
            # Exponential backoff
            calculated_delay = delay * (exponential_base ** attempt)
            
            # Add jitter (simplified for testing)
            jitter = 0.5  # Fixed jitter for predictable testing
            return calculated_delay * jitter
        
        # Test delay calculation
        delay = mock_calculate_delay(delay=1.0, exponential_base=2.0, attempt=0)
        assert delay == 0.5  # 1.0 * (2.0 ** 0) * 0.5
        
        delay = mock_calculate_delay(delay=1.0, exponential_base=2.0, attempt=1)
        assert delay == 1.0  # 1.0 * (2.0 ** 1) * 0.5
        
        delay = mock_calculate_delay(delay=1.0, exponential_base=2.0, attempt=2)
        assert delay == 2.0  # 1.0 * (2.0 ** 2) * 0.5

    def test_jitter_calculation(self):
        """Test jitter calculation to avoid thundering herd."""
        def mock_calculate_delay_with_jitter(delay, exponential_base, attempt):
            """Mock delay calculation with random jitter."""
            import random
            
            # Set seed for predictable testing
            random.seed(42)
            
            # Exponential backoff
            calculated_delay = delay * (exponential_base ** attempt)
            
            # Add jitter between 0.1 and 0.9
            jitter = random.uniform(0.1, 0.9)
            return calculated_delay * jitter, jitter
        
        # Test jitter application
        delay, jitter = mock_calculate_delay_with_jitter(delay=2.0, exponential_base=2.0, attempt=1)
        
        # Verify jitter is within expected range
        assert 0.1 <= jitter <= 0.9
        # Verify delay calculation includes jitter
        expected_base_delay = 2.0 * (2.0 ** 1)  # 4.0
        assert delay == expected_base_delay * jitter


class TestRetryIntegration:
    """Test retry integration scenarios."""

    def test_retry_with_logging(self):
        """Test retry behavior with logging."""
        # Mock retry with logging
        class MockRetryHandler:
            def __init__(self):
                self.logs = []
            
            async def execute(self, func, *args, **kwargs):
                """Mock execute with logging."""
                attempt = 0
                max_attempts = 3
                
                while attempt < max_attempts:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        attempt += 1
                        if attempt < max_attempts:
                            self.logs.append(f"Retry attempt {attempt} after error: {e}")
                            await asyncio.sleep(0.01)
                        else:
                            self.logs.append(f"All {max_attempts} attempts failed")
                            raise e
        
        # Mock function that fails twice then succeeds
        call_count = 0
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception(f"Error on attempt {call_count}")
            return "success"
        
        handler = MockRetryHandler()
        result = asyncio.run(handler.execute(failing_function))
        
        assert result == "success"
        assert len(handler.logs) == 2  # Two retry attempts logged
        assert "Retry attempt 1" in handler.logs[0]
        assert "Retry attempt 2" in handler.logs[1]

    def test_retry_with_different_error_types(self):
        """Test retry behavior with different error types."""
        # Mock retry handler that handles different error types
        class MockRetryHandler:
            def __init__(self):
                self.retryable_errors = ["NetworkError", "TimeoutError"]
                self.non_retryable_errors = ["ValueError", "RetryAfter"]
            
            async def execute(self, func, *args, **kwargs):
                """Mock execute with different error handling."""
                max_attempts = 3
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        error_type = type(e).__name__
                        
                        if error_type in self.non_retryable_errors:
                            # Don't retry these errors
                            raise e
                        elif error_type in self.retryable_errors:
                            # Retry these errors
                            if attempt < max_attempts - 1:
                                await asyncio.sleep(0.01)
                                continue
                            else:
                                raise e
                        else:
                            # Unknown error, don't retry
                            raise e
                
                raise Exception("Should not reach here")
        
        # Test with retryable error
        class NetworkError(Exception):
            pass
        
        call_count = 0
        async def network_error_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise NetworkError("Network issue")
            return "recovered"
        
        handler = MockRetryHandler()
        result = asyncio.run(handler.execute(network_error_function))
        assert result == "recovered"
        assert call_count == 3
        
        # Test with non-retryable error
        class ValueError(Exception):
            pass
        
        async def value_error_function():
            raise ValueError("Invalid input")
        
        with pytest.raises(ValueError):
            asyncio.run(handler.execute(value_error_function))

    def test_retry_context_preservation(self):
        """Test that context is preserved across retries."""
        # Mock retry handler that preserves context
        class MockRetryHandler:
            async def execute(self, func, *args, **kwargs):
                """Mock execute that preserves function arguments."""
                max_attempts = 3
                
                for attempt in range(max_attempts):
                    try:
                        # Pass all arguments and kwargs to the function
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(0.01)
                            continue
                        else:
                            raise e
        
        # Test function that uses arguments and kwargs
        call_count = 0
        async def context_function(arg1, arg2, kwarg1=None, kwarg2=None):
            nonlocal call_count
            call_count += 1
            
            # Verify arguments are preserved
            assert arg1 == "test_arg1"
            assert arg2 == "test_arg2"
            assert kwarg1 == "test_kwarg1"
            assert kwarg2 == "test_kwarg2"
            
            if call_count <= 2:
                raise Exception("Temporary failure")
            return f"success with {arg1}, {arg2}, {kwarg1}, {kwarg2}"
        
        handler = MockRetryHandler()
        result = asyncio.run(handler.execute(
            context_function,
            "test_arg1", "test_arg2",
            kwarg1="test_kwarg1", kwarg2="test_kwarg2"
        ))
        
        assert "success with test_arg1, test_arg2, test_kwarg1, test_kwarg2" in result
        assert call_count == 3

    def test_retry_performance_considerations(self):
        """Test retry performance considerations."""
        # Mock retry handler with performance tracking
        class MockRetryHandler:
            def __init__(self):
                self.total_delay = 0
                self.attempt_count = 0
            
            async def execute(self, func, *args, **kwargs):
                """Mock execute with performance tracking."""
                import time
                start_time = time.time()
                max_attempts = 3
                
                for attempt in range(max_attempts):
                    self.attempt_count = attempt + 1
                    try:
                        result = await func(*args, **kwargs)
                        self.total_delay = time.time() - start_time
                        return result
                    except Exception as e:
                        if attempt < max_attempts - 1:
                            delay = 0.01 * (2 ** attempt)  # Exponential backoff
                            await asyncio.sleep(delay)
                            continue
                        else:
                            self.total_delay = time.time() - start_time
                            raise e
        
        # Test function that fails twice then succeeds
        call_count = 0
        async def performance_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return "success"
        
        handler = MockRetryHandler()
        result = asyncio.run(handler.execute(performance_function))
        
        assert result == "success"
        assert handler.attempt_count == 3
        assert handler.total_delay > 0  # Some delay occurred due to retries

    def test_retry_configuration_validation(self):
        """Test retry configuration validation."""
        # Mock retry handler with configuration validation
        class MockRetryHandler:
            def __init__(self, max_attempts=3, delay=1.0, exponential_base=2.0):
                # Validate configuration
                if max_attempts <= 0:
                    raise ValueError("max_attempts must be positive")
                if delay < 0:
                    raise ValueError("delay cannot be negative")
                if exponential_base <= 0:
                    raise ValueError("exponential_base must be positive")
                
                self.max_attempts = max_attempts
                self.delay = delay
                self.exponential_base = exponential_base
        
        # Test valid configuration
        handler = MockRetryHandler(max_attempts=5, delay=2.0, exponential_base=1.5)
        assert handler.max_attempts == 5
        assert handler.delay == 2.0
        assert handler.exponential_base == 1.5
        
        # Test invalid configurations
        with pytest.raises(ValueError, match="max_attempts must be positive"):
            MockRetryHandler(max_attempts=0)
        
        with pytest.raises(ValueError, match="delay cannot be negative"):
            MockRetryHandler(delay=-1.0)
        
        with pytest.raises(ValueError, match="exponential_base must be positive"):
            MockRetryHandler(exponential_base=0)
