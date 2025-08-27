# tests/test_prompt.py
import pytest
import sys
from quickquestion.qq import QuickQuestion


def test_generate_prompt_format():
    """Test that the prompt is correctly formatted"""
    settings = {
        "default_provider": "LM Studio",
        "simple_mode": False,
        "default_model": "test-model"
    }
    
    qq = QuickQuestion(debug=False, settings=settings)
    
    # Test on macOS/Linux
    original_platform = sys.platform
    try:
        sys.platform = "darwin"
        prompt = qq.generate_prompt("find large files")
        
        # Check critical requirements are present
        assert "CRITICAL REQUIREMENTS:" in prompt
        assert "You MUST respond with ONLY a JSON array" in prompt
        assert "REQUIRED FORMAT" in prompt
        assert '["complete command 1", "complete command 2", "complete command 3"]' in prompt
        assert "Nothing else. Just the JSON array." in prompt
        assert "macOS" in prompt
        
        # Test on Windows
        sys.platform = "win32"
        prompt = qq.generate_prompt("find large files")
        assert "Windows" in prompt
        
    finally:
        sys.platform = original_platform


def test_prompt_includes_question():
    """Test that the user's question is included in the prompt"""
    settings = {
        "default_provider": "LM Studio",
        "simple_mode": False,
        "default_model": "test-model"
    }
    
    qq = QuickQuestion(debug=False, settings=settings)
    
    test_question = "how to recursively delete empty directories"
    prompt = qq.generate_prompt(test_question)
    
    assert test_question in prompt