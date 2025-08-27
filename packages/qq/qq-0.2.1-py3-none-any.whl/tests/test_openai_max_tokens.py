# tests/test_openai_max_tokens.py
import pytest
from unittest.mock import Mock, patch
from quickquestion.llm_lite_provider import OpenAIProvider


class TestOpenAIMaxTokens:
    """Test OpenAI provider's handling of max_tokens vs max_completion_tokens"""
    
    def test_newer_models_use_max_completion_tokens(self):
        """Test that newer models use max_completion_tokens parameter"""
        provider = OpenAIProvider()
        provider.api_key = "test-key"
        
        # Test with gpt-5 model
        provider.current_model = "gpt-5-mini-2025-08-07"
        
        with patch('quickquestion.llm_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '["cmd1", "cmd2", "cmd3"]'
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            result = provider.generate_response("test prompt")
            
            # Check the request data
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            
            # Debug output
            print(f"Model: {provider.current_model}")
            print(f"Request data: {request_data}")
            
            # Should have max_completion_tokens, not max_tokens
            assert 'max_completion_tokens' in request_data
            assert request_data['max_completion_tokens'] == 200
            assert 'max_tokens' not in request_data
    
    def test_older_models_use_max_tokens(self):
        """Test that older models use max_tokens parameter"""
        provider = OpenAIProvider()
        provider.api_key = "test-key"
        
        # Test with gpt-4 model
        provider.current_model = "gpt-4"
        
        with patch('quickquestion.llm_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '["cmd1", "cmd2", "cmd3"]'
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            provider.generate_response("test prompt")
            
            # Check the request data
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            
            # Should have max_tokens, not max_completion_tokens
            assert 'max_tokens' in request_data
            assert request_data['max_tokens'] == 200
            assert 'max_completion_tokens' not in request_data
    
    def test_gpt4o_uses_max_completion_tokens(self):
        """Test that gpt-4o models use max_completion_tokens"""
        provider = OpenAIProvider()
        provider.api_key = "test-key"
        
        # Test with gpt-4o model
        provider.current_model = "gpt-4o-mini"
        
        with patch('quickquestion.llm_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '["cmd1", "cmd2", "cmd3"]'
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            provider.generate_response("test prompt")
            
            # Check the request data
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            
            # Should have max_completion_tokens for gpt-4o models
            assert 'max_completion_tokens' in request_data
            assert request_data['max_completion_tokens'] == 200
            assert 'max_tokens' not in request_data
    
    def test_debug_method_uses_correct_parameter(self):
        """Test that debug method also uses correct parameter"""
        provider = OpenAIProvider(debug=True)
        provider.api_key = "test-key"
        
        # Test with gpt-5 model
        provider.current_model = "gpt-5-mini"
        
        with patch('quickquestion.llm_provider.requests.post') as mock_post:
            with patch('builtins.print'):  # Suppress debug output
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [{
                        "message": {
                            "content": '["cmd1", "cmd2", "cmd3"]'
                        }
                    }],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20}
                }
                mock_post.return_value = mock_response
                
                provider.generate_response_with_debug("test prompt")
                
                # Check the request data
                call_args = mock_post.call_args
                request_data = call_args[1]['json']
                
                # Should have max_completion_tokens for newer models
                assert 'max_completion_tokens' in request_data
                assert request_data['max_completion_tokens'] == 200
                assert 'max_tokens' not in request_data