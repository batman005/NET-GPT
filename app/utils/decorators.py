"""
Custom decorators for common patterns in Net-GPT.
Includes logging, caching, error handling, timing, and validation.
"""
import logging
import functools
import time
from typing import Any, Callable, TypeVar, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Type variable for decorators
F = TypeVar('F', bound=Callable[..., Any])


# ============================================================================
# 1. EXECUTION TIME TRACKING
# ============================================================================

def log_execution_time(func: F) -> F:
    """
    Decorator: Tracks and logs how long a function takes to execute.
    
    Usage:
        @log_execution_time
        def slow_function():
            time.sleep(2)
            return "result"
    
    Output:
        INFO: slow_function() executed in 2.05 seconds
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__}() executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__}() failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper


def log_execution_time_async(func: F) -> F:
    """
    Decorator: Tracks execution time for async functions.
    
    Usage:
        @log_execution_time_async
        async def slow_async_function():
            await asyncio.sleep(2)
            return "result"
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__}() executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__}() failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper


# ============================================================================
# 2. ERROR HANDLING & RECOVERY
# ============================================================================

def handle_errors(default_return: Any = None, log_traceback: bool = True):
    """
    Decorator: Catches exceptions and returns default value (graceful failure).
    
    Usage:
        @handle_errors(default_return="error", log_traceback=True)
        def risky_function():
            raise ValueError("Something went wrong")
            
        result = risky_function()  # Returns "error", doesn't crash
    
    Args:
        default_return: Value to return if exception occurs
        log_traceback: Whether to log full traceback
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"{func.__name__}() raised {type(e).__name__}: {str(e)}", 
                    exc_info=log_traceback
                )
                return default_return
        
        return wrapper
    
    return decorator


def handle_errors_async(default_return: Any = None, log_traceback: bool = True):
    """
    Decorator: Error handling for async functions.
    
    Usage:
        @handle_errors_async(default_return={}, log_traceback=True)
        async def risky_async_function():
            raise ValueError("Something went wrong")
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"{func.__name__}() raised {type(e).__name__}: {str(e)}", 
                    exc_info=log_traceback
                )
                return default_return
        
        return wrapper
    
    return decorator


# ============================================================================
# 3. INPUT VALIDATION
# ============================================================================

def validate_input(**validations):
    """
    Decorator: Validates function input arguments.
    
    Usage:
        @validate_input(
            question=lambda x: isinstance(x, str) and len(x) > 0,
            user_id=lambda x: isinstance(x, str)
        )
        def process_query(question: str, user_id: str):
            return f"Processing {question} for {user_id}"
        
        process_query("Show devices", "john")  # ✅ Works
        process_query("", "john")               # ❌ Raises ValueError
    
    Args:
        **validations: param_name=validation_function pairs
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each specified parameter
            for param_name, validator in validations.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for parameter '{param_name}' "
                            f"with value: {value}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# ============================================================================
# 4. SIMPLE CACHING
# ============================================================================

def cache_result(ttl_seconds: int = 3600):
    """
    Decorator: Caches function results for specified time (TTL = Time To Live).
    
    Usage:
        @cache_result(ttl_seconds=300)  # Cache for 5 minutes
        def expensive_operation(query: str):
            # Do expensive work
            return result
        
        # First call: executes function
        expensive_operation("SELECT *")
        
        # Second call (within 5 min): returns cached result
        expensive_operation("SELECT *")
        
        # Third call (after 5 min): executes function again
        expensive_operation("SELECT *")
    
    Args:
        ttl_seconds: How long to cache results
    """
    def decorator(func: F) -> F:
        cache = {}
        cache_time = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from arguments
            cache_key = str(args) + str(kwargs)
            current_time = time.time()
            
            # Check if cached result is still valid
            if cache_key in cache:
                cached_time = cache_time[cache_key]
                if current_time - cached_time < ttl_seconds:
                    logger.debug(f"{func.__name__}() returning cached result")
                    return cache[cache_key]
                else:
                    # Cache expired, remove it
                    del cache[cache_key]
                    del cache_time[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = result
            cache_time[cache_key] = current_time
            logger.debug(f"{func.__name__}() result cached for {ttl_seconds}s")
            
            return result
        
        return wrapper
    
    return decorator


# ============================================================================
# 5. FUNCTION CALL LOGGING
# ============================================================================

def log_function_call(log_args: bool = True, log_result: bool = True):
    """
    Decorator: Logs function calls with arguments and results.
    
    Usage:
        @log_function_call(log_args=True, log_result=True)
        def get_user(user_id: int, include_email: bool = False):
            return {"id": user_id, "email": "user@example.com"}
        
        get_user(123, include_email=True)
    
    Output:
        INFO: Calling get_user(user_id=123, include_email=True)
        INFO: get_user() returned: {'id': 123, 'email': 'user@example.com'}
    
    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log function result
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if log_args:
                logger.info(f"Calling {func.__name__}(*{args}, **{kwargs})")
            
            result = func(*args, **kwargs)
            
            if log_result:
                logger.info(f"{func.__name__}() returned: {result}")
            
            return result
        
        return wrapper
    
    return decorator


# ============================================================================
# 6. RATE LIMITING (Simple)
# ============================================================================

def rate_limit(max_calls: int, time_window: int = 60):
    """
    Decorator: Limits how many times function can be called in time window.
    
    Usage:
        @rate_limit(max_calls=5, time_window=60)  # Max 5 calls per minute
        def send_email(recipient: str):
            # Send email
            pass
        
        # First 5 calls work fine
        for i in range(5):
            send_email(f"user{i}@example.com")  # ✅
        
        # 6th call in same minute fails
        send_email("user5@example.com")  # ❌ Raises RuntimeError("Rate limit exceeded")
    
    Args:
        max_calls: Maximum calls allowed
        time_window: Time window in seconds
    """
    def decorator(func: F) -> F:
        call_times = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            
            # Remove old calls outside time window
            call_times[:] = [t for t in call_times if current_time - t < time_window]
            
            # Check if limit exceeded
            if len(call_times) >= max_calls:
                raise RuntimeError(
                    f"Rate limit exceeded: {max_calls} calls per {time_window}s"
                )
            
            # Record this call
            call_times.append(current_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# ============================================================================
# 7. DEPRECATED FUNCTION WARNING
# ============================================================================

def deprecated(message: str = ""):
    """
    Decorator: Warns when deprecated function is used.
    
    Usage:
        @deprecated("Use new_function() instead")
        def old_function():
            return "I'm old"
        
        old_function()  # Works but logs warning
    
    Output:
        WARNING: old_function() is deprecated. Use new_function() instead
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            msg = f"{func.__name__}() is deprecated"
            if message:
                msg += f". {message}"
            logger.warning(msg)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# ============================================================================
# 8. ASYNC TIMEOUT
# ============================================================================

def async_timeout(seconds: float):
    """
    Decorator: Timeout for async functions.
    
    Usage:
        @async_timeout(5.0)  # 5 second timeout
        async def fetch_data():
            await asyncio.sleep(10)
            return "data"
        
        await fetch_data()  # ❌ Raises TimeoutError after 5 seconds
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import asyncio
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs), 
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"{func.__name__}() timed out after {seconds}s")
                raise
        
        return wrapper
    
    return decorator
