"""Basic tests for easecloud-errica package"""

import pytest
import os
from easecloud_errica import (
    quick_setup, 
    log_info, 
    log_error, 
    get_monitoring_stats,
    __version__
)


def test_package_version():
    """Test that package has a valid version"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_basic_import():
    """Test that package can be imported successfully"""
    import easecloud_errica
    assert hasattr(easecloud_errica, 'quick_setup')
    assert hasattr(easecloud_errica, 'log_info')
    assert hasattr(easecloud_errica, 'log_error')


def test_quick_setup():
    """Test quick setup functionality"""
    # Set up test environment
    os.environ["APP_NAME"] = "Test App"
    os.environ["APP_VERSION"] = "1.0.0-test"
    
    manager, handler = quick_setup()
    
    assert manager is not None
    assert handler is not None
    
    # Test that console channel is enabled by default
    assert 'console' in manager.enabled_channels


def test_logging_functionality():
    """Test basic logging functionality"""
    os.environ["APP_NAME"] = "Test App"
    
    manager, handler = quick_setup()
    
    # Test info logging
    log_info("Test info message")
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error("Test error message", e, {"test": True})


def test_monitoring_stats():
    """Test monitoring statistics"""
    os.environ["APP_NAME"] = "Test App"
    
    manager, handler = quick_setup()
    
    stats = get_monitoring_stats()
    
    assert isinstance(stats, dict)
    assert 'errica_version' in stats
    assert stats['errica_version'] == __version__


def test_task_monitoring():
    """Test task monitoring context manager"""
    from easecloud_errica import task_monitor
    
    os.environ["APP_NAME"] = "Test App"
    manager, handler = quick_setup()
    
    with task_monitor("test_task", category="testing"):
        log_info("Task is running")
    
    # Task should complete without errors


if __name__ == "__main__":
    pytest.main([__file__])