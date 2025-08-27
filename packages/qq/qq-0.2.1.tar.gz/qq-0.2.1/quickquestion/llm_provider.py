#!/usr/bin/env python3
# llm_provider.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import requests
import json
import os
import asyncio
import aiohttp
import sys
import ssl


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
            # Unescape escaped quotes
            cmd = cmd.replace('\\"', '"').replace("\\'", "'")
            # Remove any residual JSON escaping
            cmd = cmd.replace('\\\\', '\\')
            return cmd

        try:
            # Clean up markdown formatting if present
            if content.startswith('```'):
                first_newline = content.find('\n')
                if first_newline != -1:
                    content = content[first_newline + 1:]
                if content.endswith('```'):
                    content = content[:-3]
            
            content = content.strip()
            
            # Fix truncated responses by balancing brackets
            if content.count('[') > content.count(']'):
                content = content + ']' * (content.count('[') - content.count(']'))
            
            # Try parsing as JSON first
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    # Handle nested arrays and clean up commands
                    commands = []
                    for item in parsed:
                        if isinstance(item, list):
                            commands.extend(clean_command(str(x)) for x in item)
                        else:
                            cleaned = clean_command(str(item))
                            if cleaned:
                                commands.append(cleaned)
                    return commands
                elif isinstance(parsed, dict):
                    # Handle JSON object format: {"commands": [...]}
                    for key in ['commands', 'suggestions', 'options', 'answers']:
                        if key in parsed and isinstance(parsed[key], list):
                            commands = []
                            for item in parsed[key]:
                                if isinstance(item, list):
                                    commands.extend(clean_command(str(x)) for x in item)
                                else:
                                    cleaned = clean_command(str(item))
                                    if cleaned:
                                        commands.append(cleaned)
                            if commands:
                                return commands
                    # If dict but no recognized keys, try to extract first list value
                    for value in parsed.values():
                        if isinstance(value, list):
                            commands = []
                            for item in value:
                                cleaned = clean_command(str(item))
                                if cleaned:
                                    commands.append(cleaned)
                            if commands:
                                return commands
                    raise ValueError("Response dict does not contain valid command list")
                else:
                    raise ValueError("Response is neither a list nor a dict")
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, try line-by-line
                commands = []
                for line in content.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('```'):
                        continue
                        
                    try:
                        # Try parsing line as JSON
                        line_parsed = json.loads(line)
                        if isinstance(line_parsed, list):
                            commands.extend(clean_command(cmd) for cmd in line_parsed)
                        else:
                            cleaned = clean_command(line)
                            if cleaned:
                                commands.append(cleaned)
                    except json.JSONDecodeError:
                        # If not valid JSON and looks like a command, add it
                        if not line.startswith('[') and not line.endswith(']'):
                            cleaned = clean_command(line)
                            if cleaned:
                                commands.append(cleaned)
                
                if commands:
                    return commands
                
                raise ValueError("No valid commands found in response")

        except Exception as e:
            if self.debug:
                print("DEBUG: Error parsing response:", str(e))
                print("DEBUG: Raw content:", content)
                print("DEBUG: Content type:", type(content))
                if content:
                    print("DEBUG: First few characters:", repr(content[:100]))
                    print("DEBUG: Content analysis:", self._check_special_characters(content))
            raise Exception(f"Error parsing response: {str(e)}\nRaw content: {content}")

    async def async_check_status(self, debug=False) -> bool:
        """Async version of status check with enhanced debugging"""
        if debug:
            print(f"\nDEBUG Provider: Starting async status check for {self.__class__.__name__}")

        try:
            # For SDK-based providers that don't use HTTP endpoints
            if not hasattr(self, 'api_url'):
                if debug:
                    print("DEBUG Provider: Using direct SDK connection")
                models = self.get_available_models()
                if models:
                    self.current_model = self.select_best_model(models)
                    if debug:
                        print(f"DEBUG Provider: Found models: {models}")
                        print(f"DEBUG Provider: Selected model: {self.current_model}")
                    return True
                if debug:
                    print("DEBUG Provider: No models found")
                return False

            # For HTTP API-based providers
            if debug:
                print(f"DEBUG Provider: API URL = {self.api_url}")

            try:
                async with aiohttp.ClientSession() as session:
                    if debug:
                        print("DEBUG Provider: Established aiohttp session")
                        print(f"DEBUG Provider: Attempting connection to {self.api_url}")

                    try:
                        async with session.get(self.api_url, timeout=2.0) as response:
                            if debug:
                                print(f"DEBUG Provider: Response status: {response.status}")
                                print(f"DEBUG Provider: Response headers: {dict(response.headers)}")
                            return response.status == 200
                    except asyncio.TimeoutError:
                        if debug:
                            print("DEBUG Provider: Connection timeout")
                        return False
                    except aiohttp.ClientError as e:
                        if debug:
                            print(f"DEBUG Provider: Connection error: {str(e)}")
                        return False
            except Exception as e:
                if debug:
                    print(f"DEBUG Provider: Connection error: {str(e)}")
                return False

        except Exception as e:
            if debug:
                print(f"DEBUG Provider: Unexpected error: {str(e)}")
                import traceback
                print("DEBUG Provider: Full traceback:")
                traceback.print_exc()
            return False

    def check_status(self, debug=False) -> bool:
        """Sync wrapper for async status check with debugging"""
        try:
            if debug:
                print(f"\nDEBUG Provider: Setting up async loop for {self.__class__.__name__}")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            if debug:
                print("DEBUG Provider: Created new event loop")

            result = loop.run_until_complete(self.async_check_status(debug=debug))

            if debug:
                print(f"DEBUG Provider: Async check completed with result: {result}")

            loop.close()

            if debug:
                print("DEBUG Provider: Closed event loop")

            return result
        except Exception as e:
            if debug:
                print(f"DEBUG Provider: Error in async wrapper: {str(e)}")
                import traceback
                print("DEBUG Provider: Full traceback:")
                traceback.print_exc()
            return False

    def select_best_model(self, available_models: List[str]) -> Optional[str]:
        """Select the best model from available ones based on preferences"""
        available_lower = [m.lower() for m in available_models]

        for preferred in self.PREFERRED_MODELS:
            for available in available_lower:
                if preferred in available:
                    return available_models[available_lower.index(available)]

        return available_models[0] if available_models else None

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
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass


class LMStudioProvider(LLMProvider):
    """LM Studio implementation of LLM provider"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.api_url = "http://localhost:1234/v1"
        self.current_model = None
        self.default_model = "model"

    def generate_response(self, prompt: str) -> List[str]:
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "model": self.current_model or self.default_model  # Use default if no model set
        }

        try:
            response = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_llm_response(content)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise Exception(f"Error generating response: {str(e)}")

    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "model": self.current_model or self.default_model  # Use default if no model set
        }

        try:
            print("\nDEBUG: Making request to LM Studio API...")
            print(f"DEBUG: Request URL: {self.api_url}/chat/completions")
            print(f"DEBUG: Request headers: {json.dumps(headers, indent=2)}")
            print(f"DEBUG: Request data: {json.dumps(data, indent=2)}")

            response = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=data)
            print(f"\nDEBUG: Response status code: {response.status_code}")
            
            # Handle headers that might be Mock objects in tests
            try:
                response_headers = dict(response.headers)
            except (TypeError, AttributeError):
                response_headers = {"note": "Headers not available in test environment"}
                
            print(f"DEBUG: Response headers: {json.dumps(response_headers, indent=2)}")

            response.raise_for_status()
            response_json = response.json()
            print(f"DEBUG: Response JSON: {json.dumps(response_json, indent=2)}")

            content = response_json["choices"][0]["message"]["content"]
            print(f"\nDEBUG: Raw content before parsing: {content}")

            parsed = self._parse_llm_response(content)
            print(f"\nDEBUG: Final parsed commands: {json.dumps(parsed, indent=2)}")

            return parsed

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"\nDEBUG: Error occurred: {str(e)}")
            if isinstance(e, requests.exceptions.RequestException):
                print(f"DEBUG: Full response text: {e.response.text if hasattr(e, 'response') else 'No response text'}")
            raise Exception(f"Error generating response: {str(e)}")

    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.api_url}/models")
            if response.status_code == 200:
                models = response.json()
                if models.get('data'):
                    return [model['id'] for model in models['data']]
            return []
        except requests.exceptions.RequestException:
            return []

    def check_status(self) -> bool:
        available_models = self.get_available_models()
        if available_models:
            self.current_model = self.select_best_model(available_models)
            return True
        return False

    def get_model_info(self) -> Optional[str]:
        return self.current_model


class OllamaProvider(LLMProvider):
    """Ollama implementation of LLM provider"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.api_url = "http://localhost:11434/api"
        self.current_model = None

    def get_available_models(self) -> List[str]:
        """Get available models with better error handling"""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=2.0)

            if response.status_code == 200:
                models = response.json()
                if models.get('models'):
                    return [model['name'] for model in models['models']]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {str(e)}")
            return []

    def select_best_model(self, available_models: List[str]) -> Optional[str]:
        """Enhanced model selection for Ollama"""
        available_lower = [m.lower() for m in available_models]

        # First try exact matches with preferred models
        for preferred in self.PREFERRED_MODELS:
            for available in available_lower:
                if preferred == available:
                    return available_models[available_lower.index(available)]

        # Then try partial matches
        for preferred in self.PREFERRED_MODELS:
            for available in available_lower:
                if preferred in available:
                    return available_models[available_lower.index(available)]

        # If no matches, return first available
        return available_models[0] if available_models else None

    async def async_check_status(self, debug=False) -> bool:
        """Async version of status check with enhanced error handling"""
        if debug:
            print(f"\nDEBUG Provider: Starting async status check for {self.__class__.__name__}")
            print(f"DEBUG Provider: API URL = {self.api_url}")

        try:
            async with aiohttp.ClientSession() as session:
                if debug:
                    print("DEBUG Provider: Established aiohttp session")
                    print(f"DEBUG Provider: Attempting connection to {self.api_url}/tags")

                try:
                    # Ollama uses /api/tags to list models
                    async with session.get(f"{self.api_url}/tags", timeout=2.0) as response:
                        if debug:
                            print(f"DEBUG Provider: Response status: {response.status}")
                            print(f"DEBUG Provider: Response headers: {dict(response.headers)}")

                            if response.status != 200:
                                text = await response.text()
                                print(f"DEBUG Provider: Error response: {text}")

                        # Only consider 200 as success
                        if response.status == 200:
                            models_data = await response.json()
                            if models_data.get('models'):
                                available_models = [m['name'] for m in models_data['models']]
                                if debug:
                                    print(f"DEBUG Provider: Found models: {available_models}")
                                self.current_model = self.select_best_model(available_models)
                                if debug:
                                    print(f"DEBUG Provider: Selected model: {self.current_model}")
                                return True
                            else:
                                if debug:
                                    print("DEBUG Provider: No models found in response")
                                return False

                        if debug:
                            print("DEBUG Provider: Unsuccessful status code")
                        return False

                except asyncio.TimeoutError:
                    if debug:
                        print("DEBUG Provider: Connection timeout")
                    return False
                except aiohttp.ClientError as e:
                    if debug:
                        print(f"DEBUG Provider: Connection error: {str(e)}")
                        print(f"DEBUG Provider: Is Ollama running at {self.api_url}?")
                    return False

        except Exception as e:
            if debug:
                print(f"DEBUG Provider: Unexpected error: {str(e)}")
                import traceback
                print("DEBUG Provider: Full traceback:")
                traceback.print_exc()
            return False

    def check_status(self, debug=False) -> bool:
        """Sync version of status check"""
        if debug:
            print("\nDEBUG Provider: Checking Ollama status")

        try:
            available_models = self.get_available_models()
            if available_models:
                self.current_model = self.select_best_model(available_models)
                if debug:
                    print(f"DEBUG Provider: Found models: {available_models}")
                    print(f"DEBUG Provider: Selected model: {self.current_model}")
                return True
            return False
        except Exception as e:
            if debug:
                print(f"DEBUG Provider: Error checking status: {str(e)}")
            return False

    def get_model_info(self) -> Optional[str]:
        return self.current_model

    def generate_response(self, prompt: str) -> List[str]:
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7
        }

        try:
            response = requests.post(f"{self.api_url}/generate", headers=headers, json=data)
            response.raise_for_status()
            content = response.json()["response"]
            return self._parse_llm_response(content)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise Exception(f"Error generating response: {str(e)}")

    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7
        }

        try:
            print("\nDEBUG: Making request to Ollama API...")
            print(f"DEBUG: Request URL: {self.api_url}/generate")
            print(f"DEBUG: Request headers: {json.dumps(headers, indent=2)}")
            print(f"DEBUG: Request data: {json.dumps(data, indent=2)}")

            response = requests.post(f"{self.api_url}/generate", headers=headers, json=data)
            print(f"\nDEBUG: Response status code: {response.status_code}")
            print(f"DEBUG: Response headers: {json.dumps(dict(response.headers), indent=2)}")

            response.raise_for_status()
            response_json = response.json()
            print(f"DEBUG: Response JSON: {json.dumps(response_json, indent=2)}")

            content = response_json["response"]
            print(f"\nDEBUG: Raw content before parsing: {content}")

            parsed = self._parse_llm_response(content)
            print(f"\nDEBUG: Final parsed commands: {json.dumps(parsed, indent=2)}")

            return parsed

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"\nDEBUG: Error occurred: {str(e)}")
            if isinstance(e, requests.exceptions.RequestException):
                print(f"DEBUG: Full response text: {e.response.text if hasattr(e, 'response') else 'No response text'}")
            raise Exception(f"Error generating response: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic implementation of LLM provider using the official SDK"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.current_model = None
        self.client = None
        self.available_models = []

        if not self.api_key:
            if self.debug:
                print("DEBUG: No Anthropic API key found in environment")
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)

            # Define default models - these will be used if we can't get them from the SDK
            # Updated as of January 2025
            self.available_models = [
                "claude-3-5-sonnet-20241022",  # Latest and most capable
                "claude-3-5-haiku-20241022",   # Fast and efficient
                "claude-3-opus-20240229",       # Previous flagship
                "claude-3-sonnet-20240229",     # Balanced performance
                "claude-3-haiku-20240307",      # Fastest, most compact
                "claude-2.1",                   # Legacy model
                "claude-2.0",                   # Legacy model
                "claude-instant-1.2"            # Legacy instant model
            ]

            # Try to get models from the SDK if possible
            try:
                from anthropic.types import Model
                if hasattr(Model, '__args__'):
                    union_args = Model.__args__
                    if len(union_args) > 1:
                        literal_type = union_args[1]
                        sdk_models = list(literal_type.__args__)
                        if sdk_models:
                            self.available_models = sdk_models
            except (ImportError, AttributeError, IndexError) as e:
                if self.debug:
                    print(f"DEBUG: Using default models list due to error: {str(e)}")

        except ImportError as e:
            if "anthropic" in str(e):
                print("Anthropic SDK not installed. Please install with: pip install anthropic")
            else:
                print(f"Error importing Anthropic SDK: {str(e)}")
            self.client = None
            self.available_models = []
        except Exception as e:
            print(f"Error initializing Anthropic client: {str(e)}")
            self.client = None
            self.available_models = []

    def get_available_models(self) -> List[str]:
        """Get available models - try API first, fallback to defaults"""
        if not self.api_key or not self.client:
            return []
            
        # Try to fetch from API using sync request
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            response = requests.get(
                "https://api.anthropic.com/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = []
                if isinstance(data, dict) and 'data' in data:
                    for model in data['data']:
                        if isinstance(model, dict) and 'id' in model:
                            models.append(model['id'])
                
                if models:
                    self.available_models = models
                    return models
                    
        except Exception as e:
            if self.debug:
                print(f"DEBUG Anthropic: Error fetching models from API: {str(e)}")
        
        # Return cached/default models if API fails
        return self.available_models
    
    def select_best_model(self, available_models: List[str]) -> Optional[str]:
        """Select the best Anthropic model with preference for newer versions"""
        if not available_models:
            return None
            
        # Prioritize Claude 3.5 models
        priority_order = [
            "claude-3-5-sonnet",  # Most capable
            "claude-3-5-haiku",   # Fast and efficient
            "claude-3-opus",      # Previous flagship
            "claude-3-sonnet",    # Balanced
            "claude-3-haiku",     # Fastest
            "claude-2.1",
            "claude-2.0",
            "claude-instant"
        ]
        
        # Check for matches in priority order
        for priority in priority_order:
            for model in available_models:
                if priority in model.lower():
                    return model
                    
        # If no matches, return the first available
        return available_models[0]

    async def async_get_available_models(self, debug=False) -> List[str]:
        """Fetch available models from Anthropic API"""
        if debug:
            print("DEBUG Anthropic: Checking available models from API")
        
        if not self.api_key:
            if debug:
                print("DEBUG Anthropic: No API key, returning default models")
            return self.available_models
            
        try:
            import aiohttp
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.anthropic.com/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if debug:
                            print(f"DEBUG Anthropic: API response: {data}")
                        
                        # Extract model IDs from the response
                        models = []
                        if isinstance(data, dict) and 'data' in data:
                            for model in data['data']:
                                if isinstance(model, dict) and 'id' in model:
                                    models.append(model['id'])
                        
                        if models:
                            if debug:
                                print(f"DEBUG Anthropic: Found {len(models)} models from API: {models}")
                            self.available_models = models
                            return models
                        else:
                            if debug:
                                print("DEBUG Anthropic: No models found in API response, using defaults")
                            return self.available_models
                    else:
                        if debug:
                            error_text = await response.text()
                            print(f"DEBUG Anthropic: API error {response.status}: {error_text}")
                        return self.available_models
                        
        except Exception as e:
            if debug:
                print(f"DEBUG Anthropic: Error fetching models from API: {str(e)}")
            return self.available_models

    def check_status(self) -> bool:
        if not self.api_key or not self.client:
            return False

        try:
            if self.available_models:
                self.current_model = self.select_best_model(self.available_models)
                return True
            return False
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Error checking Anthropic status: {str(e)}")
            return False

    def get_model_info(self) -> Optional[str]:
        return self.current_model

    def generate_response(self, prompt: str) -> List[str]:
        if not self.current_model:
            raise Exception("No model selected")

        try:
            message = self.client.messages.create(
                model=self.current_model,
                max_tokens=1000,  # Increased from 200 to 1000
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return self._parse_llm_response(message.content[0].text)
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        if not self.current_model:
            raise Exception("No model selected")

        try:
            print("\nDEBUG: Making request to Anthropic API...")
            print(f"DEBUG: Using model: {self.current_model}")
            print("DEBUG: Request data:", {
                "model": self.current_model,
                "max_tokens": 1000,  # Increased from 200 to 1000
                "temperature": 0.7,
                "messages": [{"role": "user", "content": prompt}]
            })

            message = self.client.messages.create(
                model=self.current_model,
                max_tokens=1000,  # Increased from 200 to 1000
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            print("\nDEBUG: Response received")
            print(f"DEBUG: Raw response: {message}")
            print(f"\nDEBUG: Raw content before parsing: {message.content[0].text}")

            parsed = self._parse_llm_response(message.content[0].text)
            print(f"\nDEBUG: Final parsed commands: {json.dumps(parsed, indent=2)}")

            return parsed

        except Exception as e:
            print(f"\nDEBUG: Error occurred: {str(e)}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            raise Exception(f"Error generating response: {str(e)}")


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1"
        self.current_model = None
        self.ssl_context = self._create_ssl_context()
        self.cert_path = self._find_cert_path()

        self.available_models = [
            "gpt-4-turbo",  # Latest GPT-4 Turbo
            "gpt-4",        # Standard GPT-4
            "gpt-4-32k",    # Extended context GPT-4
            "gpt-3.5-turbo" # Fast and efficient
        ]

    def _find_cert_path(self) -> Optional[str]:
        """Find the certificate path for requests library"""
        if sys.platform == 'darwin':
            # Try to find the certificates
            cert_paths = [
                '/usr/local/etc/openssl/cert.pem',  # Homebrew OpenSSL
                '/usr/local/etc/openssl@3/cert.pem',  # Homebrew OpenSSL 3
                '/etc/ssl/cert.pem',  # System SSL
                '/Library/Developer/CommandLineTools/usr/lib/python3/cert.pem'  # Python SSL
            ]

            for cert_path in cert_paths:
                if os.path.exists(cert_path):
                    return cert_path
        return None

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context with proper certificate handling"""
        if sys.platform == 'darwin':
            cert_path = self._find_cert_path()
            if cert_path:
                ctx = ssl.create_default_context()
                ctx.load_verify_locations(cert_path)
                return ctx

        # For non-macOS or if no cert found, use default
        return None

    async def async_check_status(self, debug=False) -> bool:
        """Enhanced async status check with proper SSL handling"""
        if debug:
            print("\nDEBUG OpenAI: Starting async status check")
            print(f"DEBUG OpenAI: Using API URL: {self.api_url}")
            print(f"DEBUG OpenAI: API key status: {'Present' if self.api_key else 'Missing'}")
            if self.ssl_context:
                print("DEBUG OpenAI: Using custom SSL context")
            else:
                print("DEBUG OpenAI: Using default SSL context")

        if not self.api_key:
            if debug:
                print("DEBUG OpenAI: Cannot proceed without API key")
            return False

        try:
            connector = None
            if self.ssl_context:
                connector = aiohttp.TCPConnector(ssl=self.ssl_context)

            timeout = aiohttp.ClientTimeout(total=10)  # Increased timeout
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                if debug:
                    print("DEBUG OpenAI: Testing API key validity with models endpoint")

                async with session.get(f"{self.api_url}/models", headers=headers) as response:
                    if debug:
                        print(f"DEBUG OpenAI: Models endpoint response status: {response.status}")
                        if response.status != 200:
                            text = await response.text()
                            print(f"DEBUG OpenAI: Error response: {text}")

                    return response.status == 200

        except aiohttp.ClientError as e:
            if debug:
                print(f"DEBUG OpenAI: Connection error: {str(e)}")
            return False
        except asyncio.TimeoutError:
            if debug:
                print("DEBUG OpenAI: Request timed out")
            return False
        except Exception as e:
            if debug:
                print(f"DEBUG OpenAI: Unexpected error: {str(e)}")
                import traceback
                print("DEBUG OpenAI: Full traceback:")
                traceback.print_exc()
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models with enhanced error handling"""
        if not self.api_key:
            return self.available_models

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"{self.api_url}/models",
                headers=headers,
                timeout=5.0
            )

            if response.status_code == 200:
                models = response.json()
                chat_models = [
                    model['id'] for model in models['data']
                    if any(preferred in model['id'] for preferred in ['gpt-5', 'gpt-4', 'gpt-3.5'])
                ]
                return chat_models if chat_models else self.available_models
            elif response.status_code == 401:
                print("OpenAI API key is invalid or expired")
                return self.available_models
            else:
                return self.available_models

        except requests.exceptions.RequestException:
            return self.available_models

    def check_status(self) -> bool:
        if not self.api_key:
            return False

        available_models = self.get_available_models()
        if available_models:
            self.current_model = self.select_best_model(available_models)
            return True
        return False

    def get_model_info(self) -> Optional[str]:
        return self.current_model

    def generate_response(self, prompt: str) -> List[str]:
        """Generate a response with proper SSL handling"""
        if not self.current_model:
            raise Exception("No model selected")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # Use max_completion_tokens for newer models
        if "gpt-5" in self.current_model or "gpt-4o" in self.current_model:
            data["max_completion_tokens"] = 200
        else:
            data["max_tokens"] = 200

        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10,
                verify=self.cert_path if self.cert_path else True
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_llm_response(content)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error generating response: {str(e)}")

    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        if not self.current_model:
            raise Exception("No model selected")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # Use max_completion_tokens for newer models
        if "gpt-5" in self.current_model or "gpt-4o" in self.current_model:
            data["max_completion_tokens"] = 200
        else:
            data["max_tokens"] = 200

        try:
            print("\nDEBUG: Making request to OpenAI API...")
            print(f"DEBUG: Request URL: {self.api_url}/chat/completions")

            # Mask the API key in debug output
            debug_headers = headers.copy()
            debug_headers["Authorization"] = "Bearer ***"
            print(f"DEBUG: Request headers: {json.dumps(debug_headers, indent=2)}")
            print(f"DEBUG: Request data: {json.dumps(data, indent=2)}")

            response = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=data)
            print(f"\nDEBUG: Response status code: {response.status_code}")

            response.raise_for_status()
            response_json = response.json()

            # Only log essential parts of the response
            debug_response = {
                'choices': [{
                    'message': response_json['choices'][0]['message']
                }],
                'usage': response_json['usage']
            }
            print(f"DEBUG: Response (truncated): {json.dumps(debug_response, indent=2)}")

            content = response_json["choices"][0]["message"]["content"]
            print(f"\nDEBUG: Raw content before parsing: {content}")

            # Check for special characters using the base class method
            char_analysis = self._check_special_characters(content)
            print("\nDEBUG: Content analysis:")
            for key, value in char_analysis.items():
                print(f"DEBUG: {key}: {value}")

            # Handle markdown code blocks
            if char_analysis["starts_with_markdown"] and char_analysis["ends_with_markdown"]:
                print("DEBUG: Detected markdown code block, cleaning...")
                content = content.strip('`')
                if content.startswith('json\n'):
                    content = content[5:]
                content = content.strip()
                print("DEBUG: Content after markdown cleanup:", content)

            # Use the standard parsing method which includes thinking tag filtering
            print("\nDEBUG: Calling _parse_llm_response...")
            parsed = self._parse_llm_response(content)
            
            print("\nDEBUG: Final parsed commands:", json.dumps(parsed, indent=2))
            return parsed

        except Exception as e:
            print("\nDEBUG: Error occurred:", str(e))
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
                print("DEBUG: Full response text:", e.response.text)
            import traceback
            print("DEBUG: Full traceback:", traceback.print_exc())
            raise Exception(f"Error generating response: {str(e)}")


class GroqProvider(LLMProvider):
    """Groq implementation of LLM provider using their OpenAI-compatible API"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1"
        self.current_model = None

    def get_available_models(self) -> List[str]:
        """Fetch available models from Groq API"""
        if not self.api_key:
            return []

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(f"{self.api_url}/models", headers=headers)
            response.raise_for_status()

            models_data = response.json()
            # Filter to get only text models (exclude whisper and vision models)
            text_models = [
                model["id"] for model in models_data["data"]
                if not any(x in model["id"].lower() for x in ["whisper", "vision"]) and model["active"]
            ]

            # Sort to ensure newer models appear first
            text_models.sort(reverse=True)
            return text_models

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Groq models: {str(e)}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing Groq models response: {str(e)}")
            return []

    def check_status(self) -> bool:
        """Check if the provider is available and ready"""
        if not self.api_key:
            return False

        try:
            models = self.get_available_models()
            if models:
                self.current_model = self.select_best_model(models)
                return True
            return False
        except Exception:
            return False

    def get_model_info(self) -> Optional[str]:
        """Get information about the currently loaded model"""
        return self.current_model

    def generate_response(self, prompt: str) -> List[str]:
        """Generate a response from the model"""
        if not self.current_model:
            raise Exception("No model selected")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        try:
            response = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            # Handle Groq's reasoning models which put content in 'reasoning' field
            message = response.json()["choices"][0]["message"]
            content = message.get("content", "")
            
            # For models that use reasoning field (like openai/gpt-oss-20b)
            if not content and "reasoning" in message:
                reasoning = message["reasoning"]
                # Extract command suggestions from reasoning
                import re
                # Look for JSON array pattern in reasoning
                json_match = re.search(r'\[[\s\S]*?\]', reasoning)
                if json_match:
                    try:
                        # Try to parse the matched JSON array
                        potential_json = json_match.group(0)
                        parsed = json.loads(potential_json)
                        if isinstance(parsed, list) and len(parsed) >= 3:
                            # Filter to only include items that look like commands
                            commands = [cmd for cmd in parsed if isinstance(cmd, str) and (
                                cmd.strip().startswith(('curl', 'wget', 'ls', 'find', 'grep', 'awk', 'sed', 'cat', 'echo', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'touch', 'chmod', 'chown', 'ps', 'kill', 'top', 'df', 'du', 'tar', 'zip', 'unzip', 'ssh', 'scp', 'git', 'npm', 'yarn', 'python', 'pip', 'ruby', 'gem', 'docker', 'kubectl')) or
                                ' -' in cmd or  # Has flags
                                '|' in cmd or   # Has pipes
                                '>' in cmd or   # Has redirection
                                '<' in cmd or
                                '&&' in cmd or
                                ';' in cmd
                            )]
                            if len(commands) >= 3:
                                content = json.dumps(commands[:3])
                            else:
                                # If not enough valid commands, try another approach
                                raise ValueError("Not enough valid commands")
                    except:
                        pass
                
                # If JSON array extraction failed, look for numbered commands
                if not content:
                    # Look for numbered list items (1), 2), 3) or 1. 2. 3.
                    numbered_pattern = r'(?:^|\n)\s*\d+[)\.]\s*(.+?)(?=\n\s*\d+[)\.]|\n\n|$)'
                    numbered_items = re.findall(numbered_pattern, reasoning, re.MULTILINE | re.DOTALL)
                    if numbered_items:
                        # Clean up the items and filter for actual commands
                        commands = []
                        for item in numbered_items:
                            # Remove any trailing explanation after the command
                            item = item.strip()
                            # If it looks like a command, add it
                            if item and not item.startswith(('But', 'However', 'Note', 'This', 'The')):
                                commands.append(item)
                        if len(commands) >= 3:
                            content = json.dumps(commands[:3])
                
                # If numbered list extraction failed, look for commands by pattern
                if not content:
                    # Look for complete commands (starting with common command names)
                    cmd_pattern = r'(?:^|\n|"|\')\s*((?:curl|wget|ls|find|grep|awk|sed|cat|echo|cd|mkdir|rm|cp|mv|touch|chmod|chown|ps|kill|top|df|du|tar|zip|unzip|ssh|scp|git|npm|yarn|python|pip|ruby|gem|docker|kubectl)\s+[^\n"\']+?)(?=\n|"|\'|$)'
                    found_commands = re.findall(cmd_pattern, reasoning, re.MULTILINE)
                    if len(found_commands) >= 3:
                        content = json.dumps(found_commands[:3])
                    else:
                        # Fallback: return empty content to trigger normal error handling
                        content = ""

            # Handle markdown code blocks
            if content.startswith('```') and content.endswith('```'):
                content = content.strip('`')
                if content.startswith('json\n'):
                    content = content[5:]
            content = content.strip()

            return self._parse_llm_response(content)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to Groq API: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Error parsing Groq response: {str(e)}")

    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        if not self.current_model:
            raise Exception("No model selected")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        try:
            print("\nDEBUG: Making request to Groq API...")
            print(f"DEBUG: Request URL: {self.api_url}/chat/completions")

            # Mask the API key in debug output
            debug_headers = headers.copy()
            debug_headers["Authorization"] = "Bearer ***"
            print(f"DEBUG: Request headers: {json.dumps(debug_headers, indent=2)}")
            print(f"DEBUG: Request data: {json.dumps(data, indent=2)}")

            response = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=data)
            print(f"\nDEBUG: Response status code: {response.status_code}")
            print(f"DEBUG: Response headers: {json.dumps(dict(response.headers), indent=2)}")

            response.raise_for_status()
            response_json = response.json()
            print(f"DEBUG: Response JSON: {json.dumps(response_json, indent=2)}")

            # Handle Groq's reasoning models which put content in 'reasoning' field
            message = response_json["choices"][0]["message"]
            content = message.get("content", "")
            
            # For models that use reasoning field (like openai/gpt-oss-20b)
            if not content and "reasoning" in message:
                reasoning = message["reasoning"]
                print(f"\nDEBUG: Model returned reasoning instead of content: {reasoning}")
                # Extract command suggestions from reasoning
                import re
                # Look for JSON array pattern in reasoning
                json_match = re.search(r'\[[\s\S]*?\]', reasoning)
                if json_match:
                    try:
                        # Try to parse the matched JSON array
                        potential_json = json_match.group(0)
                        parsed = json.loads(potential_json)
                        if isinstance(parsed, list) and len(parsed) >= 3:
                            # Filter to only include items that look like commands
                            commands = [cmd for cmd in parsed if isinstance(cmd, str) and (
                                cmd.strip().startswith(('curl', 'wget', 'ls', 'find', 'grep', 'awk', 'sed', 'cat', 'echo', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'touch', 'chmod', 'chown', 'ps', 'kill', 'top', 'df', 'du', 'tar', 'zip', 'unzip', 'ssh', 'scp', 'git', 'npm', 'yarn', 'python', 'pip', 'ruby', 'gem', 'docker', 'kubectl')) or
                                ' -' in cmd or  # Has flags
                                '|' in cmd or   # Has pipes
                                '>' in cmd or   # Has redirection
                                '<' in cmd or
                                '&&' in cmd or
                                ';' in cmd
                            )]
                            if len(commands) >= 3:
                                content = json.dumps(commands[:3])
                            else:
                                # If not enough valid commands, try another approach
                                raise ValueError("Not enough valid commands")
                    except:
                        pass
                
                # If JSON array extraction failed, look for numbered commands
                if not content:
                    # Look for numbered list items (1), 2), 3) or 1. 2. 3.
                    numbered_pattern = r'(?:^|\n)\s*\d+[)\.]\s*(.+?)(?=\n\s*\d+[)\.]|\n\n|$)'
                    numbered_items = re.findall(numbered_pattern, reasoning, re.MULTILINE | re.DOTALL)
                    if numbered_items:
                        # Clean up the items and filter for actual commands
                        commands = []
                        for item in numbered_items:
                            # Remove any trailing explanation after the command
                            item = item.strip()
                            # If it looks like a command, add it
                            if item and not item.startswith(('But', 'However', 'Note', 'This', 'The')):
                                commands.append(item)
                        if len(commands) >= 3:
                            content = json.dumps(commands[:3])
                
                # If numbered list extraction failed, look for commands by pattern
                if not content:
                    # Look for complete commands (starting with common command names)
                    cmd_pattern = r'(?:^|\n|"|\')\s*((?:curl|wget|ls|find|grep|awk|sed|cat|echo|cd|mkdir|rm|cp|mv|touch|chmod|chown|ps|kill|top|df|du|tar|zip|unzip|ssh|scp|git|npm|yarn|python|pip|ruby|gem|docker|kubectl)\s+[^\n"\']+?)(?=\n|"|\'|$)'
                    found_commands = re.findall(cmd_pattern, reasoning, re.MULTILINE)
                    if len(found_commands) >= 3:
                        content = json.dumps(found_commands[:3])
                    else:
                        # Fallback: return empty content to trigger normal error handling
                        content = ""
                        
            print("\nDEBUG: Raw content before parsing:", content)

            # Check for special characters using the base class method
            char_analysis = self._check_special_characters(content)
            print("\nDEBUG: Content analysis:")
            for key, value in char_analysis.items():
                print(f"DEBUG: {key}: {value}")

            # Handle markdown code blocks
            if char_analysis["starts_with_markdown"] and char_analysis["ends_with_markdown"]:
                print("DEBUG: Detected markdown code block, cleaning...")
                content = content.strip('`')
                if content.startswith('json\n'):
                    content = content[5:]
                content = content.strip()
                print("DEBUG: Content after markdown cleanup:", content)

            # Use the standard parsing method which includes thinking tag filtering
            print("\nDEBUG: Calling _parse_llm_response...")
            parsed = self._parse_llm_response(content)
            
            print("\nDEBUG: Final parsed commands:", json.dumps(parsed, indent=2))
            return parsed

        except Exception as e:
            print("\nDEBUG: Error occurred:", str(e))
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
                print("DEBUG: Full response text:", e.response.text)
            import traceback
            print("DEBUG: Full traceback:", traceback.format_exc())
            raise Exception(f"Error generating response: {str(e)}")


class GrokProvider(LLMProvider):
    """Grok implementation of LLM provider using their API"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.api_key = os.environ.get('GROK_API_KEY')
        self.api_url = "https://api.x.ai/v1"
        self.current_model = None

    def get_available_models(self) -> List[str]:
        """Fetch available models from Grok API"""
        if not self.api_key:
            return []

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Use the correct endpoint for fetching models
            response = requests.get(f"{self.api_url}/language-models", headers=headers)
            response.raise_for_status()

            models_data = response.json()
            # Extract only the model IDs
            return [model['id'] for model in models_data['models']]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Grok models: {str(e)}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing Grok models response: {str(e)}")
            return []

    def check_status(self) -> bool:
        """Check if the provider is available and ready"""
        if not self.api_key:
            return False

        try:
            models = self.get_available_models()
            if models:
                self.current_model = self.select_best_model(models)
                return True
            return False
        except Exception:
            return False

    def get_model_info(self) -> Optional[str]:
        """Get information about the currently loaded model"""
        return self.current_model

    def generate_response(self, prompt: str) -> List[str]:
        """Generate a response with proper SSL handling"""
        if not self.current_model:
            raise Exception("No model selected")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_llm_response(content)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error generating response: {str(e)}")

    def generate_response_with_debug(self, prompt: str) -> List[str]:
        """Generate a response from the model with debug information"""
        if not self.current_model:
            raise Exception("No model selected")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        try:
            print("\nDEBUG: Making request to Grok (using OpenAI API standard)...")
            print(f"DEBUG: Request URL: {self.api_url}/chat/completions")

            # Mask the API key in debug output
            debug_headers = headers.copy()
            debug_headers["Authorization"] = "Bearer ***"
            print(f"DEBUG: Request headers: {json.dumps(debug_headers, indent=2)}")
            print(f"DEBUG: Request data: {json.dumps(data, indent=2)}")

            response = requests.post(f"{self.api_url}/chat/completions", headers=headers, json=data)
            print(f"\nDEBUG: Response status code: {response.status_code}")

            response.raise_for_status()
            response_json = response.json()

            # Only log essential parts of the response
            debug_response = {
                'choices': [{
                    'message': response_json['choices'][0]['message']
                }],
                'usage': response_json['usage']
            }
            print(f"DEBUG: Response (truncated): {json.dumps(debug_response, indent=2)}")

            content = response_json["choices"][0]["message"]["content"]
            print(f"\nDEBUG: Raw content before parsing: {content}")

            # Check for special characters using the base class method
            char_analysis = self._check_special_characters(content)
            print("\nDEBUG: Content analysis:")
            for key, value in char_analysis.items():
                print(f"DEBUG: {key}: {value}")

            # Handle markdown code blocks
            if char_analysis["starts_with_markdown"] and char_analysis["ends_with_markdown"]:
                print("DEBUG: Detected markdown code block, cleaning...")
                content = content.strip('`')
                if content.startswith('json\n'):
                    content = content[5:]
                content = content.strip()
                print("DEBUG: Content after markdown cleanup:", content)

            # Use the standard parsing method which includes thinking tag filtering
            print("\nDEBUG: Calling _parse_llm_response...")
            parsed = self._parse_llm_response(content)
            
            print("\nDEBUG: Final parsed commands:", json.dumps(parsed, indent=2))
            return parsed

        except Exception as e:
            print("\nDEBUG: Error occurred:", str(e))
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
                print("DEBUG: Full response text:", e.response.text)
            import traceback
            print("DEBUG: Full traceback:", traceback.print_exc())
            raise Exception(f"Error generating response: {str(e)}")
