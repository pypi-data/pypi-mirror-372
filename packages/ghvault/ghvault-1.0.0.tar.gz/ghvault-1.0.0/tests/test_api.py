# tests/test_api.py
import base64
import os
import tempfile
from unittest.mock import patch

import httpx
import pytest  # type: ignore
from nacl.public import SealedBox

from ghvault.api import (
    create_or_update_secret,
    delete_environment_secret,
    delete_multiple_secrets,
    get_gh_environment_public_key,
    get_github_token,
    libsodium_encrypt,
    list_environment_secrets,
    parse_env_file,
    set_github_token,
    validate_github_token,
    write_env_to_github,
)


class TestTokenManagement:
    """Test GitHub token management functions."""

    def test_set_github_token(self):
        """Test setting GitHub token."""
        token = "test_token_123"
        set_github_token(token)

        import ghvault.api

        assert ghvault.api.GH_TOKEN == token

    def test_get_github_token_from_global(self):
        """Test getting token from global variable."""
        token = "global_token_123"
        set_github_token(token)

        assert get_github_token() == token

    def test_get_github_token_from_env(self, mock_env_vars, mock_github_token):
        """Test getting token from environment variable."""
        # Clear global token
        import ghvault.api

        ghvault.api.GH_TOKEN = None

        assert get_github_token() == mock_github_token

    def test_get_github_token_not_available(self):
        """Test error when no token is available."""
        # Clear global token and environment
        import ghvault.api

        ghvault.api.GH_TOKEN = None

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="GitHub token not available"):
                get_github_token()


class TestTokenValidation:
    """Test GitHub token validation."""

    @patch("ghvault.api.httpx.get")
    def test_validate_github_token_success(self, mock_get, mock_user_response):
        """Test successful token validation."""
        mock_get.return_value = mock_user_response

        result = validate_github_token("valid_token")

        assert result is True
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://api.github.com/user"
        assert kwargs["headers"]["Authorization"] == "Bearer valid_token"

    @patch("ghvault.api.httpx.get")
    def test_validate_github_token_failure(self, mock_get, mock_httpx_response):
        """Test failed token validation."""
        mock_get.return_value = mock_httpx_response(status_code=401)

        result = validate_github_token("invalid_token")

        assert result is False

    @patch("ghvault.api.httpx.get")
    def test_validate_github_token_exception(self, mock_get):
        """Test token validation with network exception."""
        mock_get.side_effect = httpx.RequestError("Network error")

        result = validate_github_token("token")

        assert result is False


class TestPublicKeyRetrieval:
    """Test GitHub environment public key retrieval."""

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.get_github_token")
    def test_get_gh_environment_public_key_success(
        self, mock_get_token, mock_get, mock_public_key_response, sample_repo_info
    ):
        """Test successful public key retrieval."""
        mock_get_token.return_value = "test_token"
        mock_get.return_value = mock_public_key_response

        result = get_gh_environment_public_key(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
        )

        assert result["key"] == "base64_encoded_public_key_here"
        assert result["key_id"] == "test_key_id_123"

        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        expected_url = f"https://api.github.com/repos/{sample_repo_info['owner']}/{sample_repo_info['repo']}/environments/{sample_repo_info['environment']}/secrets/public-key"
        assert args[0] == expected_url

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.get_github_token")
    def test_get_gh_environment_public_key_cached(
        self, mock_get_token, mock_get, mock_public_key_response, sample_repo_info
    ):
        """Test that public key is cached properly."""
        mock_get_token.return_value = "test_token"
        mock_get.return_value = mock_public_key_response

        # First call
        result1 = get_gh_environment_public_key(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
        )

        # Second call should use cache
        result2 = get_gh_environment_public_key(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
        )

        assert result1 == result2
        # Should only be called once due to caching
        assert mock_get.call_count == 1

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.get_github_token")
    def test_get_gh_environment_public_key_failure(
        self, mock_get_token, mock_get, mock_httpx_response, sample_repo_info
    ):
        """Test public key retrieval failure."""
        mock_get_token.return_value = "test_token"
        mock_get.return_value = mock_httpx_response(status_code=404, text="Environment not found")

        with pytest.raises(RuntimeError, match="Failed to fetch public key"):
            get_gh_environment_public_key(
                sample_repo_info["owner"],
                sample_repo_info["repo"],
                sample_repo_info["environment"],
            )


class TestEncryption:
    """Test secret encryption functionality."""

    def test_libsodium_encrypt(self):
        """Test secret encryption with libsodium."""
        # Generate a test key pair
        from nacl.public import PrivateKey

        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        public_key_b64 = base64.b64encode(bytes(public_key)).decode("utf-8")

        secret_value = "test_secret_value"

        # Encrypt the secret
        encrypted_b64 = libsodium_encrypt(secret_value, public_key_b64)

        # Verify we can decrypt it
        encrypted_bytes = base64.b64decode(encrypted_b64)
        sealed_box = SealedBox(private_key)
        decrypted = sealed_box.decrypt(encrypted_bytes)

        assert decrypted.decode("utf-8") == secret_value

    def test_libsodium_encrypt_invalid_key(self):
        """Test encryption with invalid public key."""
        with pytest.raises(Exception):
            libsodium_encrypt("secret", "invalid_base64_key")


class TestSecretManagement:
    """Test secret creation and management."""

    @patch("ghvault.api.httpx.put")
    @patch("ghvault.api.get_gh_environment_public_key")
    @patch("ghvault.api.get_github_token")
    def test_create_or_update_secret_success(
        self,
        mock_get_token,
        mock_get_pk,
        mock_put,
        mock_httpx_response,
        sample_repo_info,
    ):
        """Test successful secret creation/update."""
        mock_get_token.return_value = "test_token"
        mock_get_pk.return_value = {
            "key": base64.b64encode(b"x" * 32).decode("utf-8"),  # Valid 32-byte key
            "key_id": "test_key_id",
        }
        mock_put.return_value = mock_httpx_response(status_code=201)

        result = create_or_update_secret(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            "TEST_SECRET",
            "secret_value",
        )

        # Verify API call was made
        mock_put.assert_called_once()
        args, kwargs = mock_put.call_args

        # Check URL
        expected_url = f"https://api.github.com/repos/{sample_repo_info['owner']}/{sample_repo_info['repo']}/environments/{sample_repo_info['environment']}/secrets/TEST_SECRET"
        assert args[0] == expected_url

        # Check payload structure
        payload = kwargs["json"]
        assert "encrypted_value" in payload
        assert payload["key_id"] == "test_key_id"

    @patch("ghvault.api.httpx.put")
    @patch("ghvault.api.get_gh_environment_public_key")
    @patch("ghvault.api.get_github_token")
    def test_create_or_update_secret_failure(
        self,
        mock_get_token,
        mock_get_pk,
        mock_put,
        mock_httpx_response,
        sample_repo_info,
    ):
        """Test secret creation failure."""
        mock_get_token.return_value = "test_token"
        mock_get_pk.return_value = {
            "key": base64.b64encode(b"x" * 32).decode("utf-8"),
            "key_id": "test_key_id",
        }
        mock_put.return_value = mock_httpx_response(status_code=403, text="Forbidden")

        with pytest.raises(RuntimeError, match="Failed to set secret"):
            create_or_update_secret(
                sample_repo_info["owner"],
                sample_repo_info["repo"],
                sample_repo_info["environment"],
                "TEST_SECRET",
                "secret_value",
            )


class TestEnvFileParsing:
    """Test .env file parsing functionality."""

    def test_parse_env_file_success(self, temp_env_file):
        """Test successful .env file parsing."""
        result = parse_env_file(str(temp_env_file))

        expected = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "API_KEY": "test_api_key_123",
            "DEBUG": "true",
            "EMPTY_VALUE": "",
            "QUOTED_VALUE": "quoted string",
            "SINGLE_QUOTED": "single quoted",
        }

        assert result == expected

    def test_parse_env_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            parse_env_file("/nonexistent/file.env")

    def test_parse_env_file_invalid_format(self):
        """Test parsing file with invalid lines."""
        content = """VALID_KEY=valid_value
invalid_line_without_equals
=empty_key
ANOTHER_VALID=value"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()

            try:
                result = parse_env_file(f.name)
                expected = {"VALID_KEY": "valid_value", "ANOTHER_VALID": "value"}
                assert result == expected
            finally:
                os.unlink(f.name)


class TestBulkOperations:
    """Test bulk secret operations."""

    @patch("ghvault.api.parse_env_file")
    def test_write_env_to_github_dry_run(self, mock_parse, sample_repo_info):
        """Test dry run mode for bulk upload."""
        mock_parse.return_value = {"SECRET_ONE": "value1", "SECRET_TWO": "value2"}

        result = write_env_to_github(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            "/fake/path.env",
            dry_run=True,
        )

        assert result["dry_run"] is True
        assert set(result["variables"]) == {"SECRET_ONE", "SECRET_TWO"}

    @patch("ghvault.api.httpx.put")
    @patch("ghvault.api.get_gh_environment_public_key")
    @patch("ghvault.api.get_github_token")
    @patch("ghvault.api.parse_env_file")
    def test_write_env_to_github_success(
        self,
        mock_parse,
        mock_get_token,
        mock_get_pk,
        mock_put,
        mock_httpx_response,
        sample_repo_info,
    ):
        """Test successful bulk upload."""
        mock_parse.return_value = {"SECRET_ONE": "value1", "SECRET_TWO": "value2"}
        mock_get_token.return_value = "test_token"
        mock_get_pk.return_value = {
            "key": base64.b64encode(b"x" * 32).decode("utf-8"),
            "key_id": "test_key_id",
        }
        mock_put.return_value = mock_httpx_response(status_code=201)

        result = write_env_to_github(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            "/fake/path.env",
            dry_run=False,
        )

        assert len(result["success"]) == 2
        assert len(result["failed"]) == 0
        assert result["total"] == 2
        assert mock_put.call_count == 2


class TestSecretListing:
    """Test secret listing functionality."""

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.get_github_token")
    def test_list_environment_secrets_success(
        self, mock_get_token, mock_get, mock_secrets_list_response, sample_repo_info
    ):
        """Test successful secret listing."""
        mock_get_token.return_value = "test_token"
        mock_get.return_value = mock_secrets_list_response

        result = list_environment_secrets(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
        )

        expected = ["SECRET_ONE", "SECRET_TWO", "SECRET_THREE"]
        assert result == expected

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.get_github_token")
    def test_list_environment_secrets_empty(self, mock_get_token, mock_get, mock_httpx_response, sample_repo_info):
        """Test listing when no secrets exist."""
        mock_get_token.return_value = "test_token"
        mock_get.return_value = mock_httpx_response(status_code=200, json_data={"total_count": 0, "secrets": []})

        result = list_environment_secrets(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
        )

        assert result == []

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.get_github_token")
    def test_list_environment_secrets_failure(self, mock_get_token, mock_get, mock_httpx_response, sample_repo_info):
        """Test secret listing failure."""
        mock_get_token.return_value = "test_token"
        mock_response = mock_httpx_response(status_code=404)
        mock_response.json.return_value = {"message": "Environment not found"}
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="Environment not found"):
            list_environment_secrets(
                sample_repo_info["owner"],
                sample_repo_info["repo"],
                sample_repo_info["environment"],
            )


class TestSecretDeletion:
    """Test secret deletion functionality."""

    @patch("ghvault.api.httpx.delete")
    @patch("ghvault.api.get_github_token")
    def test_delete_environment_secret_success(
        self, mock_get_token, mock_delete, mock_httpx_response, sample_repo_info
    ):
        """Test successful secret deletion."""
        mock_get_token.return_value = "test_token"
        mock_delete.return_value = mock_httpx_response(status_code=204)

        result = delete_environment_secret(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            "TEST_SECRET",
        )

        assert result is True

        # Verify API call
        mock_delete.assert_called_once()
        args, kwargs = mock_delete.call_args
        expected_url = f"https://api.github.com/repos/{sample_repo_info['owner']}/{sample_repo_info['repo']}/environments/{sample_repo_info['environment']}/secrets/TEST_SECRET"
        assert args[0] == expected_url

    @patch("ghvault.api.httpx.delete")
    @patch("ghvault.api.get_github_token")
    def test_delete_environment_secret_not_found(
        self, mock_get_token, mock_delete, mock_httpx_response, sample_repo_info
    ):
        """Test deleting non-existent secret."""
        mock_get_token.return_value = "test_token"
        mock_delete.return_value = mock_httpx_response(status_code=404)

        with pytest.raises(RuntimeError, match="Secret 'TEST_SECRET' not found"):
            delete_environment_secret(
                sample_repo_info["owner"],
                sample_repo_info["repo"],
                sample_repo_info["environment"],
                "TEST_SECRET",
            )

    @patch("ghvault.api.delete_environment_secret")
    def test_delete_multiple_secrets_success(self, mock_delete_single, sample_repo_info):
        """Test successful bulk deletion."""
        mock_delete_single.return_value = True

        secret_names = ["SECRET_ONE", "SECRET_TWO", "SECRET_THREE"]

        result = delete_multiple_secrets(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            secret_names,
            confirm=True,
        )

        assert len(result["success"]) == 3
        assert len(result["failed"]) == 0
        assert result["total"] == 3
        assert mock_delete_single.call_count == 3

    @patch("ghvault.api.delete_environment_secret")
    def test_delete_multiple_secrets_partial_failure(self, mock_delete_single, sample_repo_info):
        """Test bulk deletion with some failures."""
        # First call succeeds, second fails, third succeeds
        mock_delete_single.side_effect = [True, RuntimeError("Secret not found"), True]

        secret_names = ["SECRET_ONE", "SECRET_TWO", "SECRET_THREE"]

        result = delete_multiple_secrets(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            secret_names,
            confirm=True,
        )

        assert len(result["success"]) == 2
        assert len(result["failed"]) == 1
        assert result["total"] == 3
        assert result["failed"][0]["name"] == "SECRET_TWO"

    def test_delete_multiple_secrets_empty_list(self, sample_repo_info):
        """Test bulk deletion with empty secret list."""
        result = delete_multiple_secrets(
            sample_repo_info["owner"],
            sample_repo_info["repo"],
            sample_repo_info["environment"],
            [],
            confirm=True,
        )

        assert result["total"] == 0
        assert len(result["success"]) == 0
        assert len(result["failed"]) == 0
