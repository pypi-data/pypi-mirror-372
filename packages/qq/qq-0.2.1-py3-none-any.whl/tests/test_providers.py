# tests/test_providers.py
import pytest
import json
from unittest.mock import Mock, patch
from quickquestion.llm_lite_provider import (
    LMStudioProvider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GroqProvider,
    GrokProvider
)


def test_provider_initialization():
    """Test that providers can be initialized"""
    providers = [
        LMStudioProvider(),
        OllamaProvider(),
        OpenAIProvider(),
        AnthropicProvider(),
        GroqProvider(),
        GrokProvider()
    ]
    for provider in providers:
        assert provider is not None
        assert hasattr(provider, 'debug')


def test_provider_model_selection():
    """Test model selection logic"""
    provider = LMStudioProvider()
    test_models = ["mistral-7b", "llama2-7b", "neural-chat-7b", "unknown-model"]
    selected = provider.select_best_model(test_models)
    assert selected == "mistral-7b"  # Should select mistral as it's first in PREFERRED_MODELS


def test_empty_model_list():
    """Test behavior with empty model list"""
    provider = LMStudioProvider()
    selected = provider.select_best_model([])
    assert selected is None


def test_parse_llm_response():
    """Test response parsing"""
    provider = LMStudioProvider()
    
    # Test JSON array response
    json_response = '["command1", "command2", "command3"]'
    parsed = provider._parse_llm_response(json_response)
    assert len(parsed) == 3
    assert parsed == ["command1", "command2", "command3"]
    
    # Test markdown wrapped response
    markdown_response = '```json\n["command1", "command2"]\n```'
    parsed = provider._parse_llm_response(markdown_response)
    assert len(parsed) == 2
    assert parsed == ["command1", "command2"]
    
    # Test JSON object format (new format)
    json_object_response = '{"commands": ["cmd1", "cmd2", "cmd3"]}'
    parsed = provider._parse_llm_response(json_object_response)
    assert len(parsed) == 3
    assert parsed == ["cmd1", "cmd2", "cmd3"]
    
    # Test nested arrays
    nested_response = '[["cmd1"], "cmd2", ["cmd3"]]'
    parsed = provider._parse_llm_response(nested_response)
    assert len(parsed) == 3
    assert parsed == ["cmd1", "cmd2", "cmd3"]


def test_filter_thinking_tags():
    """Test thinking tag filtering"""
    provider = LMStudioProvider()
    
    # Test various thinking tag formats
    content_with_think = 'Before command <think>This is internal thought</think> ls -la'
    filtered = provider._filter_thinking_tags(content_with_think)
    assert filtered == "Before command  ls -la"
    
    content_with_thinking = '<thinking>Planning the response</thinking>["ls", "pwd", "cd"]'
    filtered = provider._filter_thinking_tags(content_with_thinking)
    assert filtered == '["ls", "pwd", "cd"]'
    
    # Test case insensitive
    content_mixed_case = '<THINK>Internal</THINK>command<Think>More</Think>'
    filtered = provider._filter_thinking_tags(content_mixed_case)
    assert filtered == "command"
    
    # Test multiline thinking tags
    content_multiline = '''Response here
<thinking>
Multiple
Lines
Of thinking
</thinking>
More response'''
    filtered = provider._filter_thinking_tags(content_multiline)
    assert "<thinking>" not in filtered
    assert "Multiple" not in filtered
    

@pytest.mark.skip(reason="Needs LiteLLM mocking refactor")
def test_groq_reasoning_field_extraction():
    """Test Groq provider's handling of reasoning field"""
    provider = GroqProvider()
    
    # Mock response with reasoning field
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "",
                "reasoning": '''Commands to list files:
1) ls -la
2) ls -lh  
3) find . -type f -ls

These commands will show files with permissions'''
            }
        }]
    }
    
    with patch('requests.post', return_value=mock_response):
        # We need to set a model and API key for the test
        provider.current_model = "test-model"
        provider.api_key = "test-key"
        
        result = provider.generate_response("list files")
        assert len(result) == 3
        assert "ls -la" in result[0]
        assert "ls -lh" in result[1]
        assert "find . -type f -ls" in result[2]


@pytest.mark.skip(reason="Needs LiteLLM mocking refactor") 
def test_groq_reasoning_with_curl_commands():
    """Test Groq reasoning extraction with curl commands"""
    provider = GroqProvider()
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "",
                "reasoning": '''Use curl -H "Authorization: Bearer $API_KEY". The endpoint is https://api.example.com/v1/models.

Commands:
1) curl -s https://api.example.com/v1/models -H "Authorization: Bearer $API_KEY"
2) curl -X GET https://api.example.com/v1/models -H "Authorization: Bearer $API_KEY"
3) curl https://api.example.com/v1/models -H "Authorization: Bearer $API_KEY" -H "Accept: application/json"'''
            }
        }]
    }
    
    with patch('requests.post', return_value=mock_response):
        provider.current_model = "test-model"
        provider.api_key = "test-key"
        
        result = provider.generate_response("curl command for API")
        assert len(result) == 3
        assert all("curl" in cmd for cmd in result)
        assert all("https://api.example.com/v1/models" in cmd for cmd in result)