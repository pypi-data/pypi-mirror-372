# tests/test_settings_manager.py
import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock
from quickquestion.settings_manager import get_settings


@pytest.fixture
def temp_settings_file(temp_home):
    """Create a temporary settings file"""
    settings_path = Path(temp_home) / ".qq_settings.json"
    yield settings_path
    if settings_path.exists():
        settings_path.unlink()


def test_default_settings_structure():
    """Test that default settings include all required fields"""
    with patch('pathlib.Path.exists', return_value=False):
        settings = get_settings()
        
        # Check all required fields exist
        assert "default_provider" in settings
        assert "provider_options" in settings
        assert "command_action" in settings
        assert "command_action_options" in settings
        assert "simple_mode" in settings
        assert "simple_mode_action" in settings
        assert "simple_mode_action_options" in settings
        assert "default_model" in settings
        assert "available_models" in settings
        
        # Check default values
        assert settings["simple_mode"] is False
        assert settings["simple_mode_action"] == "Copy"
        assert settings["simple_mode_action_options"] == ["Copy", "Type"]


def test_get_settings_creates_default(temp_settings_file):
    """Test that get_settings creates default settings file"""
    # Ensure file doesn't exist
    assert not temp_settings_file.exists()
    
    with patch('quickquestion.settings_manager.Path.home', return_value=temp_settings_file.parent):
        settings = get_settings()
        
        # Check defaults are returned
        assert settings["simple_mode"] is False
        assert settings["simple_mode_action"] == "Copy"
        assert "provider_options" in settings


def test_get_settings_with_existing_file(temp_settings_file):
    """Test loading settings from existing file"""
    # Create a settings file with custom values
    test_settings = {
        "default_provider": "Groq",
        "simple_mode": True,
        "simple_mode_action": "Type",
        "default_model": "test-model"
    }
    
    with open(temp_settings_file, 'w') as f:
        json.dump(test_settings, f)
    
    with patch('quickquestion.settings_manager.Path.home', return_value=temp_settings_file.parent):
        settings = get_settings()
        
        assert settings["default_provider"] == "Groq"
        assert settings["simple_mode"] is True
        assert settings["simple_mode_action"] == "Type"


def test_get_settings_debug_output(temp_settings_file, capsys):
    """Test debug output from get_settings"""
    with patch('quickquestion.settings_manager.Path.home', return_value=temp_settings_file.parent):
        settings = get_settings(debug=True)
        
        captured = capsys.readouterr()
        assert "DEBUG Settings: Loading settings" in captured.out


def test_settings_backward_compatibility(temp_settings_file):
    """Test that old settings files are upgraded with new fields"""
    # Create old-style settings without simple mode fields
    old_settings = {
        "default_provider": "OpenAI",
        "command_action": "Run Command",
        "default_model": "gpt-4"
    }
    
    # Write old settings directly
    with open(temp_settings_file, 'w') as f:
        json.dump(old_settings, f)
    
    with patch('quickquestion.settings_manager.Path.home', return_value=temp_settings_file.parent):
        # Load settings - should add missing fields
        settings = get_settings()
        
        # Check that new fields were added with defaults
        assert "simple_mode" in settings
        assert "simple_mode_action" in settings
        assert settings["simple_mode"] is False
        assert settings["simple_mode_action"] == "Copy"
        
        # Check that old fields were preserved
        assert settings["default_provider"] == "OpenAI"
        assert settings["default_model"] == "gpt-4"