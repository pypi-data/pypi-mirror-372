# tests/test_utils.py
import pytest
from quickquestion.utils import clear_screen, enable_debug_printing, disable_debug_printing


def test_debug_printing():
    """Test debug printing functions"""
    # Test enabling debug printing
    enable_debug_printing()
    
    # Test disabling debug printing
    disable_debug_printing()
    
    # Verify no errors occur
    assert True


def test_clear_screen():
    """Test clear screen functionality"""
    # Just verify it doesn't raise an exception
    try:
        clear_screen()
        assert True
    except Exception as e:
        pytest.fail(f"clear_screen raised an exception: {e}")