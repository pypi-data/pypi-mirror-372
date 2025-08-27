"""
Monitoring context managers and utilities for error tracking
"""

import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from .error_handler import get_error_handler, capture_exception, capture_message


# Global monitoring state
_monitoring_enabled = False
_channel_manager = None


def setup_monitoring(channel_manager=None) -> bool:
    """
    Setup Errica with channel manager
    
    Args:
        channel_manager: Channel manager instance for notifications
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    global _monitoring_enabled, _channel_manager
    
    try:
        _channel_manager = channel_manager
        _monitoring_enabled = True
        
        # Set channel manager in error handler if it exists
        error_handler = get_error_handler()
        if error_handler and channel_manager:
            error_handler.set_channel_manager(channel_manager)
        
        return True
    except Exception as e:
        print(f"Failed to setup Errica: {e}")
        return False


class ErricaMonitoring:
    """Errica monitoring utility class"""
    
    @classmethod
    def set_context(cls, **kwargs):
        """Set context for error reporting"""
        error_handler = get_error_handler()
        if error_handler:
            error_handler.set_context(**kwargs)
    
    @classmethod
    def add_context(cls, **kwargs):
        """Add to existing context"""
        error_handler = get_error_handler()
        if error_handler:
            error_handler.add_context(**kwargs)
    
    @classmethod
    def clear_context(cls):
        """Clear current context"""
        error_handler = get_error_handler()
        if error_handler:
            error_handler.clear_context()
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get monitoring statistics"""
        error_handler = get_error_handler()
        stats = {
            "monitoring_enabled": _monitoring_enabled,
            "has_channel_manager": _channel_manager is not None,
            "has_error_handler": error_handler is not None
        }
        
        if error_handler:
            stats.update(error_handler.get_stats())
        
        if _channel_manager and hasattr(_channel_manager, 'get_stats'):
            stats["channel_manager"] = _channel_manager.get_stats()
        
        return stats
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if monitoring is enabled"""
        return _monitoring_enabled
    
    @classmethod
    def get_channel_manager(cls):
        """Get the current channel manager"""
        return _channel_manager


@contextmanager
def task_monitor(task_name: str, category: str = "general", context: Optional[Dict] = None):
    """
    Context manager for task monitoring
    
    Args:
        task_name: Name of the task being monitored
        category: Category of the task
        context: Additional context information
    
    Usage:
        with task_monitor("user_registration", category="auth", context={"user_id": 123}):
            # Your task code here
            register_user()
    """
    start_time = datetime.now()
    
    try:
        # Set context in error handler
        task_context = {"task_name": task_name, "category": category, "start_time": start_time.isoformat()}
        if context:
            task_context.update(context)
        
        ErricaMonitoring.add_context(**task_context)
        
        # Send task start notification if enabled
        if _channel_manager and hasattr(_channel_manager, 'send_task_start'):
            _channel_manager.send_task_start(task_name, category, context)
        
        yield
        
        # Send task completion notification
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if _channel_manager and hasattr(_channel_manager, 'send_task_complete'):
            _channel_manager.send_task_complete(task_name, category, duration, context)
            
    except Exception as e:
        # Calculate duration even for failed tasks
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Enhance context with task failure information
        error_context = {
            "task_name": task_name, 
            "category": category, 
            "duration": duration,
            "failed": True
        }
        if context:
            error_context.update(context)
        
        # Send task error notification
        if _channel_manager and hasattr(_channel_manager, 'send_task_error'):
            _channel_manager.send_task_error(task_name, e, error_context)
        else:
            # Fallback to direct exception capture
            capture_exception(e, error_context, f"task_{task_name}")
        
        raise
    finally:
        # Clear task-specific context
        ErricaMonitoring.clear_context()


@contextmanager  
def batch_monitor(batch_name: str, category: str = "batch", batch_size: Optional[int] = None):
    """
    Context manager for batch processing monitoring
    
    Args:
        batch_name: Name of the batch being processed
        category: Category of the batch
        batch_size: Size of the batch (optional)
    
    Usage:
        with batch_monitor("user_emails", category="notifications", batch_size=100):
            # Your batch processing code here
            send_batch_emails()
    """
    context = {"batch_size": batch_size} if batch_size else None
    with task_monitor(batch_name, category, context):
        yield


@contextmanager
def error_context(**kwargs):
    """
    Context manager for setting error context
    
    Args:
        **kwargs: Context key-value pairs
    
    Usage:
        with error_context(user_id=123, operation="payment"):
            # Your code here
            process_payment()
    """
    try:
        # Set context in error handler
        ErricaMonitoring.add_context(**kwargs)
        yield
    finally:
        # Note: We don't clear context here as it might be used by outer contexts
        # Context clearing is handled by task_monitor or explicitly by the user
        pass


def capture_task_error(task_id: str, error: Exception, context: Optional[Dict] = None):
    """
    Capture task-specific errors manually
    
    Args:
        task_id: Identifier for the task
        error: The exception that occurred
        context: Additional context information
    """
    error_context = {"task_id": task_id}
    if context:
        error_context.update(context)
    
    # Send via channel manager if available
    if _channel_manager and hasattr(_channel_manager, 'send_task_error'):
        _channel_manager.send_task_error(task_id, error, error_context)
    else:
        # Fallback to direct capture
        capture_exception(error, error_context, f"task_{task_id}")


def capture_custom_error(message: str, severity: str = "ERROR", context: Optional[Dict] = None):
    """
    Capture custom error messages
    
    Args:
        message: Error message
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        context: Additional context information
    """
    # Send via channel manager if available
    if _channel_manager and hasattr(_channel_manager, 'send_custom_message'):
        _channel_manager.send_custom_message(message, severity, context)
    else:
        # Fallback to direct capture
        capture_message(message, severity, context, "custom_error")


def send_custom_alert(message: str, severity: str = "INFO", 
                     context: Optional[Dict] = None, channels: Optional[list] = None):
    """
    Send a custom alert to specific channels
    
    Args:
        message: Alert message
        severity: Severity level
        context: Additional context information
        channels: Specific channels to send to (if None, uses routing rules)
    """
    if _channel_manager:
        if hasattr(_channel_manager, 'send_to_channels') and channels:
            _channel_manager.send_to_channels(message, severity, context, channels)
        elif hasattr(_channel_manager, 'send_custom_message'):
            _channel_manager.send_custom_message(message, severity, context)
        else:
            capture_message(message, severity, context, "custom_alert")
    else:
        capture_message(message, severity, context, "custom_alert")


def monitor_function(func):
    """
    Decorator for function monitoring
    
    Usage:
        @monitor_function
        def my_function():
            # Your function code here
            pass
    """
    def wrapper(*args, **kwargs):
        with task_monitor(func.__name__, category="function"):
            return func(*args, **kwargs)
    return wrapper


def monitor_async_function(func):
    """
    Decorator for async function monitoring
    
    Usage:
        @monitor_async_function
        async def my_async_function():
            # Your async function code here
            pass
    """
    async def wrapper(*args, **kwargs):
        with task_monitor(func.__name__, category="async_function"):
            return await func(*args, **kwargs)
    return wrapper


def test_monitoring():
    """Test monitoring functionality"""
    if _channel_manager:
        try:
            # Test with a simple message
            send_custom_alert("Errica monitoring test", "INFO", {"test": True})
            return True
        except Exception as e:
            print(f"Errica monitoring test failed: {e}")
            return False
    else:
        print("No channel manager available for testing")
        return False


# Convenience aliases
task_context = task_monitor
batch_context = batch_monitor