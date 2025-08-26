# tests/conftest.py
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest  # type: ignore


@pytest.fixture
def mock_github_token():
    """Fixture to provide a mock GitHub token."""
    return "ghp_test_token_123456789"


@pytest.fixture
def mock_env_vars(mock_github_token):
    """Fixture to mock environment variables."""
    with patch.dict(os.environ, {"GH_TOKEN": mock_github_token}, clear=False):
        yield


@pytest.fixture
def temp_env_file():
    """Fixture to create a temporary .env file for testing."""
    content = """# Test environment file
DATABASE_URL=postgresql://user:pass@localhost:5432/testdb
API_KEY=test_api_key_123
DEBUG=true
EMPTY_VALUE=
# This is a comment
QUOTED_VALUE="quoted string"
SINGLE_QUOTED='single quoted'
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(content)
        f.flush()
        yield Path(f.name)

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def temp_secrets_file():
    """Fixture to create a temporary secrets file for bulk delete testing."""
    content = """SECRET_ONE
SECRET_TWO
# This is a comment
SECRET_THREE

SECRET_FOUR
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        f.flush()
        yield Path(f.name)

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def mock_httpx_response():
    """Fixture to create mock httpx responses."""

    def _create_response(status_code=200, json_data=None, text=""):
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = text
        response.raise_for_status = Mock()

        if status_code >= 400:
            error = httpx.HTTPStatusError(message=f"HTTP {status_code}", request=Mock(), response=response)
            response.raise_for_status.side_effect = error

        return response

    return _create_response


@pytest.fixture
def mock_public_key_response(mock_httpx_response):
    """Fixture for GitHub public key API response."""
    return mock_httpx_response(
        status_code=200,
        json_data={
            "key": "base64_encoded_public_key_here",
            "key_id": "test_key_id_123",
        },
    )


@pytest.fixture
def mock_user_response(mock_httpx_response):
    """Fixture for GitHub user API response."""
    return mock_httpx_response(status_code=200, json_data={"login": "testuser", "id": 12345, "type": "User"})


@pytest.fixture
def mock_secrets_list_response(mock_httpx_response):
    """Fixture for GitHub secrets list API response."""
    return mock_httpx_response(
        status_code=200,
        json_data={
            "total_count": 3,
            "secrets": [
                {"name": "SECRET_ONE", "created_at": "2023-01-01T00:00:00Z"},
                {"name": "SECRET_TWO", "created_at": "2023-01-02T00:00:00Z"},
                {"name": "SECRET_THREE", "created_at": "2023-01-03T00:00:00Z"},
            ],
        },
    )


@pytest.fixture
def sample_repo_info():
    """Fixture providing sample repository information."""
    return {"owner": "testowner", "repo": "testrepo", "environment": "staging"}


@pytest.fixture(autouse=True)
def reset_global_state():
    """Fixture to reset global state before each test."""
    # Reset the global token and cache in api module
    from ghvault.api import PK_CACHE

    PK_CACHE.clear()

    # Reset global token
    import ghvault.api

    ghvault.api.GH_TOKEN = None

    yield

    # Cleanup after test
    PK_CACHE.clear()
    ghvault.api.GH_TOKEN = None
