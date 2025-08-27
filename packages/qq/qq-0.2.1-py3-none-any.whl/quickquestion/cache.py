import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class ProviderCache:
    _instance = None

    def __new__(cls, debug=False):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, debug=False):
        if self._initialized:
            self.debug = debug
            return

        self.debug = debug
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self.cache_file = Path.home() / '.qq_cache.json'
        self.ttl_settings = {
            'providers': 3600,  # 1 hour for provider configuration
            'models': 3600,    # 1 hour for model lists
            'default': 30      # 30 seconds for everything else
        }
        self._initialized = True
        self._load_cache()

    def _provider_to_dict(self, provider: Any) -> dict:
        """Convert provider object to serializable dictionary with \
            complete model info"""
        # Get the models first if possible
        available_models = []
        try:
            if hasattr(provider, 'get_available_models'):
                models = provider.get_available_models()
                if models:
                    available_models = models
                    if self.debug:
                        print(f"DEBUG Cache: Captured {len(models)} \
                              models for {provider.__class__.__name__}")
        except Exception as e:
            if self.debug:
                print(f"DEBUG Cache: Error getting models for \
                      {provider.__class__.__name__}: {str(e)}")

        # Build the provider data - exclude non-serializable attributes
        provider_data = {
            'type': provider.__class__.__name__,
            'model': getattr(provider, 'current_model', None),
            'available_models': available_models,
            'api_url': getattr(provider, 'api_url', None),
            'api_key': getattr(provider, 'api_key', None) if hasattr(provider, 'api_key') else None,
            'status': {
                'last_check': time.time(),
                'available': bool(available_models),
                'error': None
            }
        }

        if self.debug:
            print(f"DEBUG Cache: Serialized provider {provider_data['type']} \
                  with model {provider_data['model']}")
            if provider_data['available_models']:
                print(f"DEBUG Cache: Available models: \
                      {provider_data['available_models']}")

        return provider_data

    def _dict_to_provider(self, data: dict) -> Any:
        """Convert dictionary back to provider object with enhanced \
            model handling"""
        from quickquestion.llm_lite_provider import (
            LMStudioProvider,
            OllamaProvider,
            OpenAIProvider,
            AnthropicProvider,
            GroqProvider,
            GrokProvider
        )

        provider_map = {
            'LMStudioProvider': LMStudioProvider,
            'OllamaProvider': OllamaProvider,
            'OpenAIProvider': OpenAIProvider,
            'AnthropicProvider': AnthropicProvider,
            'GroqProvider': GroqProvider,
            'GrokProvider': GrokProvider
        }

        if self.debug:
            print(f"DEBUG Cache: Reconstructing provider {data['type']}")

        provider_class = provider_map.get(data['type'])
        if not provider_class:
            if self.debug:
                print(f"DEBUG Cache: Unknown provider type: {data['type']}")
            return None

        try:
            provider = provider_class(debug=self.debug)
            provider.current_model = data.get('model')
            provider.available_models = data.get('available_models', [])
            if 'api_url' in data and data['api_url']:
                provider.api_url = data['api_url']
            if 'api_key' in data and data['api_key']:
                provider.api_key = data['api_key']

            if self.debug:
                print(f"DEBUG Cache: Reconstructed {data['type']} with model \
                      {provider.current_model}")
                if provider.available_models:
                    print(f"DEBUG Cache: Restored \
                          {len(provider.available_models)} models")

            return provider

        except Exception as e:
            if self.debug:
                print(f"DEBUG Cache: Error reconstructing provider \
                      {data['type']}: {str(e)}")
            return None

    def _serialize_providers(self, providers: List[Any]) -> List[dict]:
        """Convert list of provider objects to serializable format"""
        return [self._provider_to_dict(p) for p in providers if p]

    def _deserialize_providers(self, data: List[dict]) -> List[Any]:
        """Convert list of dictionaries back to provider objects"""
        if self.debug:
            print(f"DEBUG Cache: Deserializing {len(data)} providers")

        providers = []
        for provider_data in data:
            try:
                provider = self._dict_to_provider(provider_data)
                if provider:
                    if self.debug:
                        print(f"DEBUG Cache: Successfully deserialized \
                              {provider_data['type']}")
                        if provider.current_model:
                            print(f"DEBUG Cache: Restored model: \
                                  {provider.current_model}")
                        if provider.available_models:
                            print(f"DEBUG Cache: Restored \
                                  {len(provider.available_models)} models")
                    providers.append(provider)
                else:
                    if self.debug:
                        print(f"DEBUG Cache: Failed to deserialize \
                              {provider_data['type']}")
            except Exception as e:
                if self.debug:
                    print(f"DEBUG Cache: Error deserializing provider \
                          {provider_data.get('type', 'unknown')}: {str(e)}")
                continue

        if self.debug:
            print(f"DEBUG Cache: Successfully deserialized \
                  {len(providers)} providers")

        return providers

    def _load_cache(self):
        """Load cache from disk with debug info"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._cache = data.get('cache', {})
                    self._timestamps = {k: float(v) for k, v
                                        in data.get('timestamps', {}).items()}

                    # Convert provider data back to objects
                    if 'available_providers' in self._cache:
                        self._cache['available_providers'] = self._deserialize_providers(
                            self._cache['available_providers'])

                if self.debug:
                    print(f"DEBUG Cache: Loaded cache from {self.cache_file}")
                    print("DEBUG Cache: Current cache contents:", self._cache.keys())
            except Exception as e:
                if self.debug:
                    print(f"DEBUG Cache: Error loading cache: {str(e)}")
                self._cache = {}
                self._timestamps = {}
        else:
            if self.debug:
                print("DEBUG Cache: No cache file found at", self.cache_file)

    def _save_cache(self):
        """Save cache to disk with enhanced error handling"""
        try:
            # Convert provider objects to serializable format
            cache_copy = self._cache.copy()
            if 'available_providers' in cache_copy:
                providers_data = []
                for provider in cache_copy['available_providers']:
                    try:
                        provider_data = self._provider_to_dict(provider)
                        if provider_data:
                            providers_data.append(provider_data)
                    except Exception as e:
                        if self.debug:
                            print(f"DEBUG Cache: Error serializing \
                                  provider: {str(e)}")
                            continue
                cache_copy['available_providers'] = providers_data

            with open(self.cache_file, 'w') as f:
                json.dump({
                    'cache': cache_copy,
                    'timestamps': self._timestamps
                }, f, indent=2)

            if self.debug:
                print(f"DEBUG Cache: Saved cache to {self.cache_file}")
                if 'available_providers' in cache_copy:
                    print("DEBUG Cache: Saved providers:", [p['type'] for p in providers_data])

        except Exception as e:
            if self.debug:
                print(f"DEBUG Cache: Error saving cache: {str(e)}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with debug info"""
        if key in self._cache:
            ttl = self.ttl_settings.get(
                next((k for k in self.ttl_settings if k in key), 'default')
            )
            age = time.time() - self._timestamps[key]

            if self.debug:
                print(f"DEBUG Cache: Found key '{key}' (age: {age:.1f}s, ttl: {ttl}s)")

            if age < ttl:
                if self.debug:
                    print(f"DEBUG Cache: Returning cached value for '{key}'")
                return self._cache[key]
            else:
                if self.debug:
                    print(f"DEBUG Cache: Entry '{key}' has expired")
                del self._cache[key]
                del self._timestamps[key]
                self._save_cache()
        else:
            if self.debug:
                print(f"DEBUG Cache: Key '{key}' not found in cache")
        return None

    def set(self, key: str, value: Any):
        """Set value in cache with debug info"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
        if self.debug:
            print(f"DEBUG Cache: Setting key '{key}' in cache")
        self._save_cache()

    def clear(self, key_prefix: Optional[str] = None):
        """Clear cache entries with debug info"""
        if key_prefix:
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(key_prefix)]
            if self.debug:
                print(f"DEBUG Cache: Clearing entries with prefix '{key_prefix}':", keys_to_delete)
            for k in keys_to_delete:
                del self._cache[k]
                del self._timestamps[k]
        else:
            if self.debug:
                print("DEBUG Cache: Clearing entire cache")
            self._cache.clear()
            self._timestamps.clear()
        self._save_cache()

    def get_cache_info(self) -> Dict[str, Dict[str, float]]:
        """Get information about cache entries"""
        current_time = time.time()
        cache_info = {}

        for key in self._cache:
            ttl = self.ttl_settings.get(
                next((k for k in self.ttl_settings if k in key), 'default')
            )
            age = current_time - self._timestamps[key]

            cache_info[key] = {
                'age_seconds': age,
                'expires_in_seconds': ttl - age,
                'ttl': ttl
            }

        return cache_info


# Global cache instance - now with debug mode support
def get_provider_cache(debug=False) -> ProviderCache:
    """Get or create the provider cache instance with debug mode"""
    return ProviderCache(debug=debug)


# Initialize the global cache instance
provider_cache = ProviderCache()
