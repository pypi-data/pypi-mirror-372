# conftest.py

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch


def pytest_configure(config):
    """Configure test environment"""
    # Set up CI mode if TEST_MODE environment variable is set to 'ci'
    pytest.is_ci = os.environ.get('TEST_MODE') == 'ci'

@pytest.fixture
def temp_home():
    """Fixture to provide a temporary home directory"""
    original_home = os.environ.get('HOME')
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['HOME'] = temp_dir
        yield Path(temp_dir)
        if original_home:
            os.environ['HOME'] = original_home

@pytest.fixture
def mock_provider_cache(temp_home):
    """Fixture to provide a clean provider cache"""
    from quickquestion.cache import ProviderCache
    cache = ProviderCache()
    cache.clear()
    return cache

# Modified AsyncContextManagerMock with proper sync/async support
class AsyncContextManagerMock:
    """Mock for async context managers"""
    def __init__(self):
        self.status = 200
        self.headers = {}
        self._response_data = {
            "choices": [{"message": {"content": '["test command 1", "test command 2", "test command 3"]'}}],
            "models": [{"id": "test-model-1"}, {"id": "test-model-2"}],
            "data": [{"id": "test-model"}]
        }

    # Sync context manager methods
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    # Async context manager methods
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    # Methods that can be both sync and async
    def json(self):
        return self._response_data

    async def ajson(self):
        return self._response_data

    def text(self):
        return '{"status": "ok"}'

    async def atext(self):
        return '{"status": "ok"}'

    def raise_for_status(self):
        if self.status >= 400:
            raise Exception(f"HTTP {self.status}")

class AsyncClientSessionMock:
    """Mock for aiohttp.ClientSession with both sync and async support"""
    def __init__(self, *args, **kwargs):
        self.response = AsyncContextManagerMock()
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def get(self, *args, **kwargs):
        return self.response

    async def aget(self, *args, **kwargs):
        return self.response

    def post(self, *args, **kwargs):
        return self.response

    async def apost(self, *args, **kwargs):
        return self.response

@pytest.fixture
def mock_api_clients(monkeypatch):
    """Mock API clients for both sync and async use"""
    if not pytest.is_ci:
        yield
        return

    # Mock response data
    mock_response_data = {
        "choices": [{"message": {"content": '["test command 1", "test command 2", "test command 3"]'}}],
        "models": [{"id": "test-model-1"}, {"id": "test-model-2"}],
        "data": [{"id": "test-model"}]
    }

    # Mock synchronous requests
    mock_response = Mock()
    mock_response.status_code = 200
    # Set headers as a real dict instead of Mock
    mock_response.headers = {
        "content-type": "application/json",
        "server": "test-server"
    }
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None

    import requests
    monkeypatch.setattr(requests, 'post', Mock(return_value=mock_response))
    monkeypatch.setattr(requests, 'get', Mock(return_value=mock_response))

    # Create session mock instance
    session_mock = AsyncClientSessionMock()

    # Mock asynchronous aiohttp
    import aiohttp
    monkeypatch.setattr(aiohttp, 'ClientSession', lambda *args, **kwargs: session_mock)

    yield session_mock

@pytest.fixture(autouse=True)
def auto_mock_api_clients(mock_api_clients):
    """Automatically apply API client mocks"""
    pass

@pytest.fixture
def mock_provider():
    """Fixture to provide a mock LLM provider"""
    provider = Mock()
    provider.get_available_models.return_value = ["test-model"]
    provider.check_status.return_value = True
    provider.current_model = "test-model"
    provider.generate_response.return_value = ["test command 1", "test command 2", "test command 3"]
    return provider