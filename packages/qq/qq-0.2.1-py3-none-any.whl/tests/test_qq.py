# tests/test_qq.py

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from quickquestion.qq import QuickQuestion
from quickquestion.ui_library import UIOptionDisplay
import subprocess


@pytest.fixture
def mock_ui():
    """Mock UI components"""
    with patch('quickquestion.qq.UIOptionDisplay') as mock_ui:
        ui_instance = Mock()
        mock_ui.return_value = ui_instance
        yield ui_instance


@pytest.fixture
def mock_clipboard():
    """Mock clipboard operations"""
    with patch('quickquestion.qq.copy_to_clipboard') as mock_copy:
        yield mock_copy


@pytest.fixture
def qq_instance(temp_home, mock_provider_cache):
    """Create a QuickQuestion instance with mocked components"""
    settings = {
        "default_provider": "LM Studio",
        "command_action": "Run Command",
        "default_model": "test-model",
        "simple_mode": False,
        "simple_mode_action": "Copy",
        "available_models": ["test-model"]
    }
    with patch('quickquestion.qq.get_settings', return_value=settings):
        qq = QuickQuestion(debug=True, settings=settings)
        yield qq


def test_display_suggestions_basic(qq_instance, mock_ui):
    """Test basic command suggestion display"""
    # Setup mock UI responses
    mock_ui.display_options.return_value = (0, 'select')  # Select first option
    
    suggestions = ["find . -type f -size +100M", "du -sh * | sort -hr", "ls -lS"]
    question = "how to find large files"
    
    # Execute display_suggestions
    qq_instance.display_suggestions(suggestions, question)
    
    # Verify UI interactions
    mock_ui.display_banner.assert_called_once()
    mock_ui.display_options.assert_called_once()
    
    # Verify header panels were created correctly
    call_args = mock_ui.display_options.call_args[1]
    header_panels = call_args.get('header_panels', [])
    assert len(header_panels) == 2
    assert "Provider Info" in header_panels[0]['title']
    assert question in header_panels[1]['content']


def test_display_suggestions_copy_command(qq_instance, mock_ui, mock_clipboard):
    """Test copy command functionality"""
    # Setup settings for copy command
    qq_instance.settings['command_action'] = 'Copy Command'
    
    # Setup mock UI responses
    mock_ui.display_options.return_value = (0, 'select')  # Select first option
    
    suggestions = ["find . -type f -size +100M"]
    
    # Execute display_suggestions and expect SystemExit
    with pytest.raises(SystemExit) as exc_info:
        qq_instance.display_suggestions(suggestions, "test")
    
    # Verify exit was successful (code 0)
    assert exc_info.value.code == 0
    
    # Verify clipboard operation
    mock_clipboard.assert_called_once_with(suggestions[0])
    
    # Verify success message
    mock_ui.display_message.assert_called_once()
    assert "copied to clipboard" in mock_ui.display_message.call_args[0][0].lower()


def test_banner_display(qq_instance, mock_ui):
    """Test banner display formatting"""
    qq_instance.print_banner()
    
    mock_ui.display_banner.assert_called_once()
    call_args = mock_ui.display_banner.call_args[0]  # Get positional arguments
    
    # Verify banner content (first arg should be title)
    assert "Quick Question" in call_args[0]
    
    # Check keyword arguments for subtitle and website
    kwargs = mock_ui.display_banner.call_args[1]
    assert 'subtitle' in kwargs
    assert 'website' in kwargs
    
    # Verify subtitle content
    subtitle = kwargs['subtitle']
    assert any("Provider:" in line for line in subtitle)
    assert any("Command Action:" in line for line in subtitle)
    
    # Verify website
    assert "southbrucke.com" in kwargs['website'].lower()


def test_get_command_suggestions(qq_instance, mock_ui):
    """Test command suggestion generation"""
    # Mock provider with both methods
    mock_provider = Mock()
    mock_provider.generate_response.return_value = ["cmd1", "cmd2", "cmd3"]
    mock_provider.generate_response_with_debug.return_value = ["cmd1", "cmd2", "cmd3"]
    mock_provider.current_model = "test-model"
    qq_instance.provider = mock_provider
    
    with patch.object(qq_instance, 'print_banner'):
        suggestions = qq_instance.get_command_suggestions("test question")
        
        # Verify suggestions format
        assert isinstance(suggestions, list)
        assert len(suggestions) == 3
        assert all(isinstance(cmd, str) for cmd in suggestions)

def test_display_suggestions_execute_command(qq_instance, mock_ui):
    """Test command execution"""
    # Setup mock UI responses
    mock_ui.display_options.return_value = (0, 'select')  # Select first option
    
    with patch('subprocess.run') as mock_run:
        suggestions = ["echo 'test'"]
        qq_instance.display_suggestions(suggestions, "test")
        
        # Verify command execution
        mock_run.assert_called_once_with(suggestions[0], shell=True)


def test_display_suggestions_navigation(qq_instance, mock_ui):
    """Test navigation through suggestions"""
    suggestions = ["cmd1", "cmd2", "cmd3"]
    
    # Simulate different navigation scenarios
    navigation_scenarios = [
        (0, 'quit'),    # Test quit
        (1, 'select'),  # Test selecting second option
        (2, 'cancel')   # Test cancel
    ]
    
    for selected, action in navigation_scenarios:
        mock_ui.display_options.return_value = (selected, action)
        
        with pytest.raises(SystemExit) if action in ('quit', 'cancel') else patch('subprocess.run'):
            qq_instance.display_suggestions(suggestions, "test")


def test_display_suggestions_cloud_provider(qq_instance, mock_ui):
    """Test display with cloud provider"""
    # Mock cloud provider
    with patch.object(qq_instance, 'is_cloud_provider', return_value=True):
        mock_ui.display_options.return_value = (0, 'quit')
        
        suggestions = ["test command"]
        
        with pytest.raises(SystemExit):
            qq_instance.display_suggestions(suggestions, "test")
        
        # Verify cloud provider indication
        call_args = mock_ui.display_options.call_args[1]
        header_panels = call_args.get('header_panels', [])
        provider_info = header_panels[0]['content']
        assert "Cloud Based Provider" in provider_info
        assert "[red]" in provider_info


def test_display_suggestions_error_handling(qq_instance, mock_ui, mock_clipboard):
    """Test error handling in suggestions display"""
    # Test clipboard error
    qq_instance.settings['command_action'] = 'Copy Command'
    mock_clipboard.side_effect = Exception("Clipboard error")
    mock_ui.display_options.return_value = (0, 'select')
    
    suggestions = ["test command"]
    
    with pytest.raises(SystemExit) as exc_info:
        qq_instance.display_suggestions(suggestions, "test")
    
    # Verify error message
    mock_ui.display_message.assert_called_once()
    error_message = mock_ui.display_message.call_args[0][0]
    assert "error" in error_message.lower()
    assert exc_info.value.code == 1

def test_command_history_integration(qq_instance, mock_ui, temp_home):
    """Test command history integration"""
    mock_ui.display_options.return_value = (0, 'select')
    
    suggestions = ["test command"]
    question = "test question"
    
    # Execute a command
    with patch('subprocess.run'):
        qq_instance.display_suggestions(suggestions, question)
    
    # Verify command was saved to history
    history_file = temp_home / '.qq_history.json'
    assert history_file.exists()
    
    import json
    with open(history_file) as f:
        history = json.load(f)
        assert len(history) > 0
        assert history[-1]['command'] == suggestions[0]
        assert history[-1]['question'] == question