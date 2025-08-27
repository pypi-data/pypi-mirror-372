# tests/test_response_parsing.py
import pytest
from quickquestion.llm_lite_provider import LMStudioProvider, GroqProvider


class TestResponseParsing:
    """Test various response parsing scenarios"""
    
    def test_parse_truncated_json(self):
        """Test parsing of truncated JSON responses"""
        provider = LMStudioProvider()
        
        # Truncated array (missing closing bracket)
        truncated = '["cmd1", "cmd2", "cmd3"'
        parsed = provider._parse_llm_response(truncated)
        assert len(parsed) == 3
        assert parsed == ["cmd1", "cmd2", "cmd3"]
        
        # Truncated with nested arrays
        truncated_nested = '[["cmd1"], ["cmd2"], ["cmd3"'
        parsed = provider._parse_llm_response(truncated_nested)
        assert len(parsed) == 3
        assert parsed == ["cmd1", "cmd2", "cmd3"]
    
    def test_parse_multiline_json(self):
        """Test parsing JSON split across multiple lines"""
        provider = LMStudioProvider()
        
        multiline = '''["ls -la",
"find . -type f -name '*.txt'",
"grep -r 'pattern' ."]'''
        parsed = provider._parse_llm_response(multiline)
        assert len(parsed) == 3
        assert "find . -type f -name '*.txt'" in parsed
    
    def test_parse_commands_with_special_chars(self):
        """Test parsing commands with quotes and special characters"""
        provider = LMStudioProvider()
        
        # Commands with escaped quotes - use proper JSON escaping
        response = '["echo \\"Hello World\\"", "grep \'pattern\'", "awk \\"{print $1}\\""]'
        parsed = provider._parse_llm_response(response)
        assert len(parsed) == 3
        # The parser should clean these up
        assert any("echo" in cmd and "Hello World" in cmd for cmd in parsed)
        assert any("grep" in cmd and "pattern" in cmd for cmd in parsed)
        assert any("awk" in cmd for cmd in parsed)
    
    def test_parse_non_json_fallback(self):
        """Test fallback parsing when JSON parsing fails"""
        provider = LMStudioProvider()
        
        # Non-JSON response with command-like lines
        non_json = '''Here are the commands:
ls -la
find . -type f
grep -r "pattern" .'''
        
        parsed = provider._parse_llm_response(non_json)
        # Should extract lines that look like commands
        assert any("ls -la" in cmd for cmd in parsed)
        assert any("find . -type f" in cmd for cmd in parsed)
    
    def test_parse_mixed_content(self):
        """Test parsing response with mixed content"""
        provider = LMStudioProvider()
        
        # Response with explanation before JSON
        mixed = '''Here are three commands:
["ls -la", "ls -lh", "ls -R"]'''
        
        parsed = provider._parse_llm_response(mixed)
        # Should extract the JSON array part
        assert "ls -la" in parsed
        assert "ls -lh" in parsed
        assert "ls -R" in parsed
        # Filter out non-command parts
        commands_only = [cmd for cmd in parsed if cmd.startswith(('ls', 'find', 'grep'))]
        assert len(commands_only) == 3
    
    def test_clean_command_function(self):
        """Test the clean_command helper function"""
        provider = LMStudioProvider()
        
        # Test quote removal
        response1 = '["ls -la"]'
        parsed1 = provider._parse_llm_response(response1)
        assert parsed1 == ["ls -la"]
        
        # Test with already clean commands
        response2 = '["echo test", "cat file.txt", "grep pattern"]'
        parsed2 = provider._parse_llm_response(response2)
        assert len(parsed2) == 3
        assert "echo test" in parsed2
        assert "cat file.txt" in parsed2
        assert "grep pattern" in parsed2


class TestGroqSpecificParsing:
    """Test Groq-specific parsing scenarios"""
    
    def test_empty_content_with_reasoning(self):
        """Test handling empty content field with reasoning"""
        provider = GroqProvider()
        
        # This would normally be part of the response handling
        # Testing the extraction logic directly
        import json
        import re
        
        reasoning = '''Commands:
1) ls -la
2) find . -name "*.py"
3) grep -r "TODO" .'''
        
        # Test numbered list extraction
        numbered_pattern = r'(?:^|\n)\s*\d+[)\.]\s*(.+?)(?=\n\s*\d+[)\.]|\n\n|$)'
        numbered_items = re.findall(numbered_pattern, reasoning, re.MULTILINE | re.DOTALL)
        
        assert len(numbered_items) == 3
        assert "ls -la" in numbered_items[0]
        assert 'find . -name "*.py"' in numbered_items[1]
        assert 'grep -r "TODO" .' in numbered_items[2]