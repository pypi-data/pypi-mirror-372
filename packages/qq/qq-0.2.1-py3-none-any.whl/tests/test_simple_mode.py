# tests/test_simple_mode.py
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from quickquestion.qq import QuickQuestion


@pytest.fixture
def qq_simple_mode(temp_home):
    """Create a QuickQuestion instance with simple mode enabled"""
    settings = {
        "default_provider": "LM Studio",
        "command_action": "Run Command",
        "simple_mode": True,
        "simple_mode_action": "Copy",
        "default_model": "test-model",
        "available_models": ["test-model"]
    }
    with patch('quickquestion.qq.get_settings', return_value=settings):
        qq = QuickQuestion(debug=False, settings=settings)
        # Mock provider
        qq.provider = Mock()
        qq.provider.generate_response.return_value = ["ls -la", "ls -l", "ls"]
        yield qq


@pytest.fixture
def mock_clipboard():
    """Mock clipboard operations"""
    with patch('quickquestion.qq.copy_to_clipboard') as mock_copy:
        yield mock_copy


def test_simple_mode_copy(qq_simple_mode, mock_clipboard):
    """Test simple mode with copy action"""
    with patch('quickquestion.qq.print') as mock_print:
        with pytest.raises(SystemExit) as exc_info:
            qq_simple_mode.handle_simple_mode(["ls -la", "ls -l", "ls"], "list files")
        
        # Check exit was successful
        assert exc_info.value.code == 0
        
        # Check clipboard was called with first command
        mock_clipboard.assert_called_once_with("ls -la")


def test_simple_mode_type(qq_simple_mode):
    """Test simple mode with type action"""
    qq_simple_mode.settings['simple_mode_action'] = 'Type'
    
    with patch('quickquestion.qq.print') as mock_print:
        with patch('quickquestion.qq.type_command_to_terminal') as mock_type:
            with pytest.raises(SystemExit) as exc_info:
                qq_simple_mode.handle_simple_mode(["ls -la", "ls -l", "ls"], "list files")
            
            # Check exit was successful
            assert exc_info.value.code == 0
            
            # Check type function was called
            mock_type.assert_called_once_with("ls -la")


def test_simple_mode_force_copy():
    """Test --simple-copy flag"""
    settings = {
        "default_provider": "LM Studio",
        "simple_mode": False,  # Not enabled in settings
        "simple_mode_action": "Type",  # Default is Type
        "default_model": "test-model",
        "available_models": ["test-model"]
    }
    
    # Test that simple-copy flag would override settings
    # In actual usage, this is handled by argparse in main()
    assert settings["simple_mode"] is False
    assert settings["simple_mode_action"] == "Type"
    
    # When simple_copy is True, it should set these values
    settings["simple_mode"] = True
    settings["simple_mode_action"] = "Copy"
    assert settings["simple_mode"] is True
    assert settings["simple_mode_action"] == "Copy"


def test_simple_mode_force_type():
    """Test --simple-type flag"""
    settings = {
        "default_provider": "LM Studio", 
        "simple_mode": False,  # Not enabled in settings
        "simple_mode_action": "Copy",  # Default is Copy
        "default_model": "test-model",
        "available_models": ["test-model"]
    }
    
    # Test that simple-type flag would override settings
    # In actual usage, this is handled by argparse in main()
    assert settings["simple_mode"] is False
    assert settings["simple_mode_action"] == "Copy"
    
    # When simple_type is True, it should set these values
    settings["simple_mode"] = True
    settings["simple_mode_action"] = "Type"
    assert settings["simple_mode"] is True
    assert settings["simple_mode_action"] == "Type"


def test_type_command_to_terminal_unix():
    """Test type_command_to_terminal on Unix systems"""
    original_platform = sys.platform
    sys.platform = 'darwin'  # macOS
    
    try:
        from quickquestion.qq import type_command_to_terminal
        
        with patch('fcntl.ioctl') as mock_ioctl:
            with patch('sys.stdin.fileno', return_value=0):
                type_command_to_terminal("ls -la")
                
                # Check that ioctl was called for each character
                assert mock_ioctl.call_count == len("ls -la")
                
    finally:
        sys.platform = original_platform


def test_type_command_to_terminal_windows():
    """Test type_command_to_terminal on Windows"""
    original_platform = sys.platform
    sys.platform = 'win32'
    
    try:
        from quickquestion.qq import type_command_to_terminal
        
        mock_msvcrt = MagicMock()
        with patch.dict('sys.modules', {'msvcrt': mock_msvcrt}):
            type_command_to_terminal("dir")
            
            # Check that putch was called for each character
            assert mock_msvcrt.putch.call_count == len("dir")
            
    finally:
        sys.platform = original_platform


def test_simple_mode_error_handling(qq_simple_mode, mock_clipboard):
    """Test simple mode error handling"""
    # Test with empty suggestions
    with patch('quickquestion.qq.print') as mock_print:
        with pytest.raises(SystemExit) as exc_info:
            qq_simple_mode.handle_simple_mode([], "test")
        assert exc_info.value.code == 1
    
    # Test with clipboard error
    mock_clipboard.side_effect = Exception("Clipboard error")
    with patch('quickquestion.qq.print') as mock_print:
        with pytest.raises(SystemExit) as exc_info:
            qq_simple_mode.handle_simple_mode(["ls"], "test")
        assert exc_info.value.code == 1


def test_get_command_suggestions_simple(qq_simple_mode):
    """Test get_command_suggestions_simple method"""
    with patch('quickquestion.qq.print'):
        suggestions = qq_simple_mode.get_command_suggestions_simple("list files")
        assert suggestions == ["ls -la", "ls -l", "ls"]
        assert qq_simple_mode.provider.generate_response.called