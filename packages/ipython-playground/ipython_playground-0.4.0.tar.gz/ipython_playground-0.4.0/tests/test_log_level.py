"""Test log level validation functionality."""

import os
from unittest import mock

from ipython_playground import _get_valid_log_level


def test_get_valid_log_level_fallback():
    """Test that invalid log levels fall back to INFO and valid ones work."""
    # Test invalid levels fall back to INFO (returns tuple with original value)
    result = _get_valid_log_level("TRACE")
    assert result == ("INFO", "TRACE")
    
    result = _get_valid_log_level("INVALID")
    assert result == ("INFO", "INVALID")
    
    # Test empty/None cases still return simple "INFO"
    assert _get_valid_log_level("") == "INFO"
    assert _get_valid_log_level(None) == "INFO"
    
    # Test valid levels work (returns just the level string)
    assert _get_valid_log_level("DEBUG") == "DEBUG"
    assert _get_valid_log_level("info") == "INFO"  # Test case insensitive


def test_module_import_with_invalid_log_level():
    """Test that the module can be imported with an invalid LOG_LEVEL without crashing."""
    with mock.patch.dict(os.environ, {"LOG_LEVEL": "TRACE"}):
        try:
            import importlib
            import ipython_playground
            importlib.reload(ipython_playground)
            success = True
        except ValueError as e:
            if "Unknown level" in str(e):
                success = False
            else:
                raise
        
        assert success, "LOG_LEVEL=TRACE should not raise 'Unknown level' ValueError"