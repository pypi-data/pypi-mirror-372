#!/usr/bin/env python3
# llm_lite_provider.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import requests
import json
import os
import asyncio
import sys
import re


class LLMProvider(ABC):
    """Base class for LLM providers"""

    PREFERRED_MODELS = [
        "mistral",
        "llama2",
        "codellama",
        "openhermes",
        "neural-chat",
        "stable-beluga",
        "qwen",
        "yi",
        "claude-3-5-sonnet",  # Add Claude 3.5 models to preferences
        "claude-3-5-haiku"
    ]

    def __init__(self, debug: bool = False):
        """Initialize the provider with debug mode"""
        self.debug = debug

    def _check_special_characters(self, content: str) -> dict:
        """Check content for special characters in a Python-version-compatible way"""
        null_byte = chr(0)  # Instead of using \x00
        newline = chr(10)   # Instead of using \n
        carriage_return = chr(13)  # Instead of using \r
        tab = chr(9)        # Instead of using \t

        return {
            "length": len(content),
            "first_chars": [ord(c) for c in content[:10]],
            "has_null_bytes": null_byte in content,
            "has_newlines": newline in content,
            "has_carriage_returns": carriage_return in content,
            "has_tabs": tab in content,
            "starts_with_markdown": content.startswith('```'),
            "ends_with_markdown": content.endswith('```'),
            "starts_with_bracket": content.startswith('['),
            "ends_with_bracket": content.endswith(']')
        }

    def _filter_thinking_tags(self, content: str) -> str:
        """Remove thinking tags and their content from the response"""
        import re
        original_content = content
        
        # Remove various thinking tag formats
        patterns = [
            r'<think>.*?</think>',
            r'<thinking>.*?</thinking>',
            r'<thought>.*?</thought>',
            r'<thoughts>.*?</thoughts>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, flags=re.DOTALL | re.IGNORECASE)
            if matches and self.debug:
                print(f"DEBUG: Filtering {len(matches)} thinking tag(s) matching pattern: {pattern}")
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        if self.debug and content != original_content:
            print(f"DEBUG: Filtered thinking tags from response")
            print(f"DEBUG: Original length: {len(original_content)}, Filtered length: {len(content)}")
        
        return content.strip()

    def _parse_llm_response(self, content: str) -> List[str]:
        """
        Enhanced response parser for LLM outputs that handles:
        - Nested array structures
        - Multiple JSON arrays on separate lines
        - Markdown code blocks
        - Escaped quotes and characters
        - Different JSON formatting styles
        - Truncated responses
        - Thinking tags removal
        """
        # Filter out thinking tags first
        content = self._filter_thinking_tags(content)
        
        def clean_command(cmd: str) -> str:
            """Clean up individual commands by removing extra quotes and escaping"""
            cmd = cmd.strip()
            # Remove wrapping quotes if present
            if (cmd.startswith('"') and cmd.endswith('"')) or \
               (cmd.startswith("'") and cmd.endswith("'")):
                cmd = cmd[1:-1]
            # Unescape common escape sequences
            cmd = cmd.replace('\\"', '"').replace("\\'", "'")
            cmd = cmd.replace('\\n', '\n').replace('\\t', '\t')
            cmd = cmd.replace('\\\\', '\\')
            return cmd

        # Handle markdown code blocks
        if content.startswith('```') and content.endswith('```'):
            content = content.strip('`')
            if content.startswith('json\n'):
                content = content[5:]
            elif content.startswith('json '):
                content = content[5:]
        content = content.strip()
        
        # Handle various empty/null cases
        if not content or content == "null" or content == "None":
            if self.debug:
                print(f"DEBUG: Content is empty/null/None, returning default commands")
            # Return sensible defaults instead of empty list
            return ["ls", "ls -la", "find . -maxdepth 1 -type f"]
        
        # First attempt: Try to parse as JSON directly
        try:
            # Check if it's wrapped in a JSON object like {"commands": [...]}
            if content.strip().startswith('{') and '"commands"' in content:
                obj = json.loads(content)
                if 'commands' in obj and isinstance(obj['commands'], list):
                    return [clean_command(str(cmd)) for cmd in obj['commands'][:3]]
            
            # Try parsing as a direct JSON array
            parsed = json.loads(content)
            if isinstance(parsed, list):
                # Handle mixed or nested arrays [[cmd1], "cmd2", [cmd3]]
                result = []
                for item in parsed[:3]:
                    if isinstance(item, list) and item:
                        result.append(clean_command(str(item[0])))
                    else:
                        result.append(clean_command(str(item)))
                return result
            elif isinstance(parsed, dict):
                # Check if there's a commands or similar key
                for key in ['commands', 'cmds', 'suggestions', 'options']:
                    if key in parsed and isinstance(parsed[key], list):
                        return [clean_command(str(cmd)) for cmd in parsed[key][:3]]
        except json.JSONDecodeError:
            pass
        
        # Second attempt: Find all JSON arrays in the content
        json_arrays = re.findall(r'\[(?:[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]', content)
        for array_str in json_arrays:
            try:
                parsed = json.loads(array_str)
                if isinstance(parsed, list) and parsed:
                    # Handle nested arrays
                    if isinstance(parsed[0], list):
                        return [clean_command(str(item[0])) for item in parsed[:3] if item]
                    return [clean_command(str(item)) for item in parsed[:3]]
            except:
                continue
        
        # Third attempt: Handle truncated JSON (missing closing bracket)
        if content.strip().startswith('['):
            truncated = content.strip()
            if not truncated.endswith(']'):
                # Try to extract complete items before truncation
                try:
                    # Add closing bracket and try to parse
                    fixed = truncated + ']'
                    parsed = json.loads(fixed)
                    if isinstance(parsed, list) and parsed:
                        return [clean_command(str(item)) for item in parsed[:3]]
                except:
                    # Extract individual quoted strings
                    quoted_strings = re.findall(r'"([^"]+)"', truncated)
                    if len(quoted_strings) >= 3:
                        return [clean_command(cmd) for cmd in quoted_strings[:3]]
        
        # Fourth attempt: Handle responses with numbered lists
        numbered_pattern = r'^\s*\d+[.)]\s*(.+)$'
        lines = content.split('\n')
        numbered_commands = []
        for line in lines:
            match = re.match(numbered_pattern, line)
            if match:
                cmd = match.group(1).strip()
                # Remove quotes if present
                if (cmd.startswith('"') and cmd.endswith('"')) or \
                   (cmd.startswith("'") and cmd.endswith("'")):
                    cmd = cmd[1:-1]
                numbered_commands.append(clean_command(cmd))
        
        if len(numbered_commands) >= 3:
            return numbered_commands[:3]
        
        # Fifth attempt: Look for commands in quoted strings across multiple lines
        # This handles cases where commands are just listed with quotes
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_commands = re.findall(quoted_pattern, content)
        if len(quoted_commands) >= 3:
            return [clean_command(cmd) for cmd in quoted_commands[:3]]
        
        # Sixth attempt: Look for backtick-quoted commands
        backtick_pattern = r'`([^`]+)`'
        backtick_commands = re.findall(backtick_pattern, content)
        if len(backtick_commands) >= 3:
            return [clean_command(cmd) for cmd in backtick_commands[:3]]
        
        # Last resort: Try to split by common delimiters
        # Look for lines that start with common command prefixes
        command_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip comments
                # Remove leading bullets, dashes, etc.
                line = re.sub(r'^[-•*>]+\s*', '', line)
                if line:
                    command_lines.append(clean_command(line))
        
        if len(command_lines) >= 3:
            return command_lines[:3]
        elif command_lines:
            return command_lines
        
        return []

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass

    @abstractmethod
    def check_status(self) -> bool:
        """Check if the provider is available"""
        pass

    @abstractmethod
    def get_model_info(self) -> Optional[str]:
        """Get information about the currently loaded model"""
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> List[str]:
        """Generate a response from the model"""
        pass

    @abstractmethod
    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        pass

    @abstractmethod
    async def async_check_status(self, debug=False) -> bool:
        """Asynchronously check if the provider is available"""
        pass

    def select_best_model(self, models: List[str]) -> str:
        """Select the best model from available ones based on preferences"""
        # Sort models to ensure consistency
        models_sorted = sorted(models)
        
        # First, try to find a preferred model
        for preferred in self.PREFERRED_MODELS:
            for model in models_sorted:
                if preferred.lower() in model.lower():
                    return model
        
        # If no preferred model found, return the first one
        return models_sorted[0] if models_sorted else None


class LiteLLMProvider(LLMProvider):
    """Universal LLM provider using LiteLLM library"""
    
    # Map provider names to LiteLLM prefixes
    PROVIDER_MAPPING = {
        "OpenAI": "openai",
        "Anthropic": "anthropic", 
        "Groq": "groq",
        "Grok": "xai",
        "Ollama": "ollama",
        "LM Studio": "openai",  # LM Studio uses OpenAI-compatible API
        "Azure": "azure",
        "Google": "vertex_ai",
        "Bedrock": "bedrock",
        "Cohere": "cohere",
        "HuggingFace": "huggingface",
        "Mistral": "mistral",
        "Replicate": "replicate"
    }
    
    def __init__(self, provider_name: str = "OpenAI", debug: bool = False):
        super().__init__(debug=debug)
        self.provider_name = provider_name
        self.litellm_prefix = self.PROVIDER_MAPPING.get(provider_name, provider_name.lower())
        self.current_model = None
        self.api_base = None
        
        # Set up API base for local providers
        if provider_name == "LM Studio":
            self.api_base = "http://localhost:1234/v1"
        elif provider_name == "Ollama":
            self.api_base = "http://localhost:11434"
            
    def get_available_models(self) -> List[str]:
        """Get available models for the provider"""
        try:
            # For local providers, try to fetch models from their APIs
            if self.provider_name == "Ollama":
                response = requests.get(f"{self.api_base}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return [model["name"] for model in models]
            elif self.provider_name == "LM Studio":
                response = requests.get(f"{self.api_base}/models")
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    return [model["id"] for model in models]
            
            # For cloud providers, return common models
            if self.provider_name == "OpenAI":
                # Try to fetch from API first
                api_key = os.environ.get('OPENAI_API_KEY')
                if api_key:
                    try:
                        headers = {"Authorization": f"Bearer {api_key}"}
                        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=5)
                        if response.status_code == 200:
                            models = response.json()
                            # Filter for chat models only, including gpt-5 models
                            chat_models = [
                                model['id'] for model in models['data']
                                if any(preferred in model['id'] for preferred in ['gpt-5-mini', 'gpt-5', 'gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo', 'chatgpt'])
                                and 'realtime' not in model['id']  # Exclude realtime models
                                and 'audio' not in model['id']  # Exclude audio models
                                and not model['id'].endswith('-preview')  # Exclude preview models
                                and 'search' not in model['id']  # Exclude search models
                                and 'transcribe' not in model['id']  # Exclude transcribe models
                                and 'tts' not in model['id']  # Exclude TTS models
                            ]
                            # Sort to ensure consistent order, with gpt-5 models first
                            chat_models.sort(key=lambda x: (not x.startswith('gpt-5'), x))
                            if chat_models:
                                return chat_models
                    except:
                        pass
                # Fallback to default models (including gpt-5)
                return ["gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            elif self.provider_name == "Anthropic":
                return ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
            elif self.provider_name == "Groq":
                return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            elif self.provider_name == "Grok":
                return ["grok-2-1212", "grok-2-vision-1212"]
            
            return []
            
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Error fetching models: {str(e)}")
            return []
    
    def check_status(self) -> bool:
        """Check if the provider is available"""
        try:
            # For local providers, check if they're running
            if self.provider_name == "Ollama":
                response = requests.get(f"{self.api_base}/api/version", timeout=2)
                if response.status_code == 200:
                    # Get models and select the smallest one if not already set
                    models = self.get_available_models()
                    if models:
                        # Only set model if not already set (preserve settings)
                        if not self.current_model:
                            self.current_model = self.select_best_model(models)
                        return True
                return False
            elif self.provider_name == "LM Studio":
                response = requests.get(f"{self.api_base}/models", timeout=2)
                if response.status_code == 200:
                    models = self.get_available_models()
                    if models:
                        # Only set model if not already set (preserve settings)
                        if not self.current_model:
                            self.current_model = self.select_best_model(models)
                        return True
                return False
            
            # For cloud providers, check if API key is set
            if self.provider_name == "OpenAI":
                return os.environ.get('OPENAI_API_KEY') is not None
            elif self.provider_name == "Anthropic":
                return os.environ.get('ANTHROPIC_API_KEY') is not None
            elif self.provider_name == "Groq":
                return os.environ.get('GROQ_API_KEY') is not None
            elif self.provider_name == "Grok":
                return os.environ.get('XAI_API_KEY') is not None
            
            # Get models and select one if not already set
            models = self.get_available_models()
            if models:
                # Only set model if not already set (preserve settings)
                if not self.current_model:
                    self.current_model = self.select_best_model(models)
                return True
            return False
        except:
            return False
    
    async def async_check_status(self, debug=False) -> bool:
        """Async status check"""
        # For now, just use sync check
        # Could be improved with aiohttp for true async
        return self.check_status()
    
    def get_model_info(self) -> Optional[str]:
        """Get current model info"""
        return self.current_model
    
    def select_best_model(self, models: List[str]) -> str:
        """Select the best model - for Ollama, prefer smallest models"""
        if self.provider_name == "Ollama" and models:
            # Define small model preferences for Ollama
            small_model_preferences = [
                "gemma2:latest",  # Smallest and fastest
                "gemma:2b",
                "tinyllama",
                "phi",
                "qwen:0.5b",
                "gemma2:2b",
                "llama3.2:1b",
                "llama3.2:3b"
            ]
            
            # Look for small models first
            for small_model in small_model_preferences:
                for model in models:
                    if small_model in model.lower():
                        return model
            
            # If no small model found, fall back to parent logic
        
        # Use parent class logic for other providers
        return super().select_best_model(models)
    
    def generate_response(self, prompt: str) -> List[str]:
        """Generate response using LiteLLM"""
        if not self.current_model:
            # Try to select a model if not already done
            models = self.get_available_models()
            if models:
                self.current_model = self.select_best_model(models)
            else:
                raise Exception("No model selected")
        
        try:
            import litellm
            
            # Configure LiteLLM settings
            litellm.drop_params = True  # Drop unsupported params automatically
            litellm.suppress_debug_info = not self.debug
            
            # Build the model string
            if self.provider_name == "LM Studio" and self.api_base:
                # LM Studio uses OpenAI-compatible API with custom base
                model = self.current_model
                extra_params = {"api_base": self.api_base}
            elif self.provider_name == "Ollama" and self.api_base:
                # Ollama uses its own API
                model = f"ollama/{self.current_model}"
                extra_params = {"api_base": self.api_base}
            elif self.provider_name == "OpenAI":
                # OpenAI doesn't need prefix, but needs explicit base_url to avoid env conflicts
                model = self.current_model
                extra_params = {"base_url": "https://api.openai.com/v1"}
            else:
                # Other cloud providers use prefix/model format
                model = f"{self.litellm_prefix}/{self.current_model}"
                extra_params = {}
            
            # Handle special cases for parameters
            params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                **extra_params
            }
            
            # Handle model-specific parameters
            if "gpt-5" in self.current_model.lower():
                # gpt-5 models only support temperature=1 and max_completion_tokens
                params["temperature"] = 1.0
                params["max_completion_tokens"] = 200
            elif "gpt-4o" in self.current_model.lower():
                # gpt-4o models use max_completion_tokens
                params["temperature"] = 0.7
                params["max_completion_tokens"] = 200
            else:
                # Default parameters
                params["temperature"] = 0.7
                params["max_tokens"] = 200
            
            # Make the completion call
            response = litellm.completion(**params)
            
            content = response.choices[0].message.content
            
            # Handle empty content (reasoning models)
            if not content and hasattr(response.choices[0].message, '_raw_response'):
                raw = response.choices[0].message._raw_response
                if isinstance(raw, dict) and 'reasoning' in raw:
                    # Extract from reasoning field similar to Groq handling
                    content = self._extract_from_reasoning(raw['reasoning'])
            
            # If still no content, log and return default
            if not content:
                if self.debug:
                    print(f"DEBUG: No content received from {self.current_model}")
                    print(f"DEBUG: Response object: {response}")
                # Return default commands for empty responses
                return ["ls", "ls -la", "find . -type f"]
            
            return self._parse_llm_response(content)
            
        except Exception as e:
            if self.debug:
                print(f"DEBUG: LiteLLM error: {str(e)}")
            raise Exception(f"Error generating response: {str(e)}")
    
    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate response with debug info"""
        if not self.current_model:
            # Try to select a model if not already done
            models = self.get_available_models()
            if models:
                self.current_model = self.select_best_model(models)
            else:
                raise Exception("No model selected")
        
        try:
            import litellm
            
            # Enable debug mode and drop unsupported params
            litellm.set_verbose = True
            litellm.drop_params = True  # Drop unsupported params automatically
            
            print(f"\nDEBUG: Using LiteLLM with provider: {self.provider_name}")
            print(f"DEBUG: Model: {self.current_model}")
            print(f"DEBUG: LiteLLM prefix: {self.litellm_prefix}")
            if self.api_base:
                print(f"DEBUG: API Base: {self.api_base}")
            
            # Build the model string and params
            if self.provider_name == "LM Studio" and self.api_base:
                model = self.current_model
                extra_params = {"api_base": self.api_base}
            elif self.provider_name == "Ollama" and self.api_base:
                model = f"ollama/{self.current_model}"
                extra_params = {"api_base": self.api_base}
            elif self.provider_name == "OpenAI":
                model = self.current_model
                extra_params = {"base_url": "https://api.openai.com/v1"}
            else:
                model = f"{self.litellm_prefix}/{self.current_model}"
                extra_params = {}
            
            print(f"DEBUG: LiteLLM model string: {model}")
            
            # Build parameters
            params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                **extra_params
            }
            
            # Handle model-specific parameters
            if "gpt-5" in self.current_model.lower():
                # GPT-5 models require temperature=1.0 and use max_completion_tokens
                params["temperature"] = 1.0
                params["max_completion_tokens"] = 200
                print(f"DEBUG: Using temperature=1.0 and max_completion_tokens for gpt-5 model")
            elif "gpt-4o" in self.current_model.lower():
                params["temperature"] = 0.7
                params["max_completion_tokens"] = 200
                print(f"DEBUG: Using max_completion_tokens for gpt-4o model")
            else:
                params["temperature"] = 0.7
                params["max_tokens"] = 200
            
            print(f"DEBUG: Request params: {json.dumps({k: v for k, v in params.items() if k != 'messages'}, indent=2)}")
            
            # Make the completion call
            response = litellm.completion(**params)
            
            print(f"\nDEBUG: Response received")
            print(f"DEBUG: Response object type: {type(response)}")
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                print(f"DEBUG: Raw content: {content}")
                print(f"DEBUG: Content type: {type(content)}")
                print(f"DEBUG: Content length: {len(content) if content else 0}")
            else:
                print("DEBUG: No choices in response or response is None")
                content = None
            
            # Handle empty content
            if not content:
                print("DEBUG: Content is empty or None")
                
                # Check for raw response
                if response and response.choices and len(response.choices) > 0:
                    if hasattr(response.choices[0].message, '_raw_response'):
                        print("DEBUG: Checking for reasoning field in raw response")
                        raw = response.choices[0].message._raw_response
                        print(f"DEBUG: Raw response type: {type(raw)}")
                        if isinstance(raw, dict):
                            print(f"DEBUG: Raw response keys: {raw.keys()}")
                            if 'reasoning' in raw:
                                content = self._extract_from_reasoning(raw['reasoning'])
                                print(f"DEBUG: Extracted from reasoning: {content}")
                
                # If still no content, use defaults
                if not content:
                    print(f"DEBUG: No content from {self.current_model}, using defaults")
                    return ["ls", "ls -la", "find . -type f"]
            
            parsed = self._parse_llm_response(content)
            print(f"\nDEBUG: Final parsed commands: {json.dumps(parsed, indent=2)}")
            
            return parsed
            
        except Exception as e:
            print(f"\nDEBUG: LiteLLM error: {str(e)}")
            import traceback
            print("DEBUG: Full traceback:")
            traceback.print_exc()
            raise Exception(f"Error generating response: {str(e)}")
    
    def _extract_from_reasoning(self, reasoning: str) -> str:
        """Extract commands from reasoning field (for models like Groq's reasoning models)"""
        # Try to find JSON array
        json_match = re.search(r'\[[\s\S]*?\]', reasoning)
        if json_match:
            return json_match.group(0)
        
        # Look for numbered lists
        numbered_pattern = r'(?:^|\n)\s*\d+[)\.]\s*(.+?)(?=\n\s*\d+[)\.]|\n\n|$)'
        numbered_items = re.findall(numbered_pattern, reasoning, re.MULTILINE | re.DOTALL)
        if numbered_items and len(numbered_items) >= 3:
            commands = [item.strip() for item in numbered_items[:3]]
            return json.dumps(commands)
        
        return ""


# Backward compatibility - create aliases for old provider classes
class LMStudioProvider(LiteLLMProvider):
    def __init__(self, debug: bool = False):
        super().__init__(provider_name="LM Studio", debug=debug)


class OllamaProvider(LiteLLMProvider):
    def __init__(self, debug: bool = False):
        super().__init__(provider_name="Ollama", debug=debug)


class OpenAIProvider(LiteLLMProvider):
    def __init__(self, debug: bool = False):
        super().__init__(provider_name="OpenAI", debug=debug)


class AnthropicProvider(LiteLLMProvider):
    def __init__(self, debug: bool = False):
        super().__init__(provider_name="Anthropic", debug=debug)


class GroqProvider(LiteLLMProvider):
    def __init__(self, debug: bool = False):
        super().__init__(provider_name="Groq", debug=debug)


class GrokProvider(LiteLLMProvider):
    def __init__(self, debug: bool = False):
        super().__init__(provider_name="Grok", debug=debug)