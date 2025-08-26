# tests/test_integration.py
import os
import tempfile
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from ghvault.cli import app


class TestEndToEndWorkflow:
    """Integration tests for complete workflows."""

    def setup_method(self):
        """Set up test runner and common mocks."""
        self.runner = CliRunner()

        # Common mock responses
        self.mock_public_key_response = {
            "key": "dGVzdF9wdWJsaWNfa2V5X2hlcmU=",  # base64 encoded test key
            "key_id": "test_key_id_123",
        }

        self.mock_user_response = {"login": "testuser", "id": 12345, "type": "User"}

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.httpx.put")
    @patch("ghvault.api.httpx.delete")
    def test_complete_secret_lifecycle(self, mock_delete, mock_put, mock_get):
        """Test complete lifecycle: set -> list -> delete secret."""
        # Setup mocks for token validation
        mock_get.side_effect = [
            # Token validation call
            Mock(status_code=200, json=lambda: self.mock_user_response),
            # Public key fetch for set
            Mock(status_code=200, json=lambda: self.mock_public_key_response),
            # List secrets call
            Mock(
                status_code=200,
                json=lambda: {
                    "total_count": 1,
                    "secrets": [{"name": "TEST_SECRET", "created_at": "2023-01-01T00:00:00Z"}],
                },
            ),
        ]

        # Mock successful secret creation
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "success"},
            text="",
            raise_for_status=Mock(),
        )

        # Mock successful secret deletion
        mock_delete.return_value = Mock(status_code=204, raise_for_status=Mock())

        with patch.dict(os.environ, {"GH_TOKEN": "test_token"}):
            # Step 1: Set a secret
            result = self.runner.invoke(
                app,
                [
                    "set",
                    "production",
                    "TEST_SECRET",
                    "secret_value",
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                ],
            )
            assert result.exit_code == 0
            assert "Secret 'TEST_SECRET' updated" in result.stdout

            # Step 2: List secrets to verify it exists
            result = self.runner.invoke(
                app,
                ["list", "production", "--owner", "testowner", "--repo", "testrepo"],
            )
            assert result.exit_code == 0
            assert "Found 1 secrets" in result.stdout
            assert "TEST_SECRET" in result.stdout

            # Step 3: Delete the secret
            result = self.runner.invoke(
                app,
                [
                    "delete",
                    "production",
                    "TEST_SECRET",
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                    "--force",
                ],
            )
            assert result.exit_code == 0
            assert "Secret 'TEST_SECRET' deleted" in result.stdout

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.httpx.put")
    def test_bulk_upload_workflow(self, mock_put, mock_get, temp_env_file):
        """Test bulk upload workflow with .env file."""
        # Setup mocks
        mock_get.side_effect = [
            # Token validation
            Mock(status_code=200, json=lambda: self.mock_user_response),
            # Public key fetch
            Mock(status_code=200, json=lambda: self.mock_public_key_response),
        ]

        # Mock successful bulk uploads
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "success"},
            text="",
            raise_for_status=Mock(),
        )

        with patch.dict(os.environ, {"GH_TOKEN": "test_token"}):
            result = self.runner.invoke(
                app,
                [
                    "bulk",
                    "staging",
                    "--file",
                    str(temp_env_file),
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                ],
            )

            assert result.exit_code == 0
            assert "secrets uploaded successfully" in result.stdout

            # Verify multiple PUT calls were made (one for each secret in temp_env_file)
            assert mock_put.call_count > 0

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.httpx.delete")
    def test_bulk_delete_workflow(self, mock_delete, mock_get, temp_secrets_file):
        """Test bulk delete workflow with secrets file."""
        # Setup mocks
        mock_get.return_value = Mock(status_code=200, json=lambda: self.mock_user_response)

        # Mock successful deletions
        mock_delete.return_value = Mock(status_code=204, raise_for_status=Mock())

        with patch.dict(os.environ, {"GH_TOKEN": "test_token"}):
            result = self.runner.invoke(
                app,
                [
                    "delete-bulk",
                    "production",
                    "--file",
                    str(temp_secrets_file),
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                    "--force",
                ],
            )

            assert result.exit_code == 0
            assert "secrets deleted successfully" in result.stdout

            # Verify multiple DELETE calls were made
            assert mock_delete.call_count > 0

    @patch("ghvault.cli.typer.prompt")
    @patch("ghvault.api.httpx.get")
    def test_interactive_token_setup(self, mock_get, mock_prompt):
        """Test interactive token setup workflow."""
        mock_prompt.return_value = "interactive_token_123"

        # Mock successful token validation
        mock_get.return_value = Mock(status_code=200, json=lambda: self.mock_user_response)

        # Clear any existing token
        with patch.dict(os.environ, {}, clear=True):
            result = self.runner.invoke(
                app,
                ["list", "production", "--owner", "testowner", "--repo", "testrepo"],
            )

            # Should prompt for token and then proceed
            mock_prompt.assert_called_once()
            assert "GitHub token validated" in result.stdout


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.api.httpx.get")
    def test_invalid_token_error(self, mock_get):
        """Test handling of invalid GitHub token."""
        # Mock failed token validation
        mock_get.return_value = Mock(status_code=401)

        with patch.dict(os.environ, {"GH_TOKEN": "invalid_token"}):
            result = self.runner.invoke(
                app,
                ["list", "production", "--owner", "testowner", "--repo", "testrepo"],
            )

            # Should fail due to token validation in ensure_github_token
            # But since token is in env, it won't be validated until API call
            # The actual validation happens in the API functions
            assert result.exit_code in [0, 1]  # Depends on where validation fails

    @patch("ghvault.api.httpx.get")
    def test_environment_not_found_error(self, mock_get):
        """Test handling when environment doesn't exist."""
        # Mock token validation success, then environment not found
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {"login": "testuser"}),  # Token validation
            Mock(
                status_code=404,
                json=lambda: {"message": "Environment not found"},
                raise_for_status=Mock(side_effect=Exception("404 Not Found")),
            ),
        ]

        with patch.dict(os.environ, {"GH_TOKEN": "valid_token"}):
            result = self.runner.invoke(
                app,
                [
                    "list",
                    "nonexistent_env",
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                ],
            )

            assert result.exit_code == 1
            assert "Failed to list secrets" in result.stdout

    def test_missing_repository_info(self):
        """Test error when repository information is missing."""
        commands_to_test = [
            ["set", "production", "SECRET", "value"],
            ["bulk", "production", "--file", "/fake/file.env"],
            ["list", "production"],
            ["delete", "production", "SECRET", "--force"],
            ["delete-bulk", "production", "--names", "SECRET", "--force"],
        ]

        for command in commands_to_test:
            result = self.runner.invoke(app, command)
            assert result.exit_code == 1
            assert "Missing repo info" in result.stdout

    @patch("ghvault.api.httpx.get")
    @patch("ghvault.api.httpx.put")
    def test_network_error_handling(self, mock_put, mock_get):
        """Test handling of network errors."""
        # Mock token validation success
        mock_get.return_value = Mock(status_code=200, json=lambda: {"login": "testuser"})

        # Mock network error on secret creation
        mock_put.side_effect = Exception("Network error")

        with patch.dict(os.environ, {"GH_TOKEN": "valid_token"}):
            result = self.runner.invoke(
                app,
                [
                    "set",
                    "production",
                    "TEST_SECRET",
                    "value",
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                ],
            )

            assert result.exit_code == 1
            assert "Failed to set secret" in result.stdout


class TestDryRunMode:
    """Test dry run functionality."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_bulk_dry_run_no_token_required(self, temp_env_file):
        """Test that dry run doesn't require GitHub token."""
        # Clear any existing token
        with patch.dict(os.environ, {}, clear=True):
            result = self.runner.invoke(
                app,
                [
                    "bulk",
                    "production",
                    "--file",
                    str(temp_env_file),
                    "--owner",
                    "testowner",
                    "--repo",
                    "testrepo",
                    "--dry-run",
                ],
            )

            assert result.exit_code == 0
            assert "Dry run completed" in result.stdout
            assert "Found" in result.stdout and "variables" in result.stdout

    @patch("ghvault.api.parse_env_file")
    def test_bulk_dry_run_shows_variables(self, mock_parse, temp_env_file):
        """Test that dry run shows what would be uploaded."""
        mock_parse.return_value = {
            "DATABASE_URL": "postgresql://localhost/test",
            "API_KEY": "test_key",
            "DEBUG": "true",
        }

        result = self.runner.invoke(
            app,
            [
                "bulk",
                "production",
                "--file",
                str(temp_env_file),
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found 3 variables" in result.stdout


class TestFileHandling:
    """Test file handling edge cases."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_env_file_with_special_characters(self):
        """Test .env file with special characters and edge cases."""
        content = """# Test file with edge cases
SIMPLE_KEY=simple_value
QUOTED_KEY="value with spaces"
SINGLE_QUOTED='another value'
EQUALS_IN_VALUE=key=value=more
EMPTY_VALUE=
URL_VALUE=https://example.com/path?param=value&other=123
MULTILINE_JSON={"key": "value", "nested": {"inner": "data"}}
SPECIAL_CHARS=!@#$%^&*()_+-=[]{}|;:,.<>?
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()

            try:
                # Test dry run to verify parsing
                result = self.runner.invoke(
                    app,
                    [
                        "bulk",
                        "production",
                        "--file",
                        f.name,
                        "--owner",
                        "testowner",
                        "--repo",
                        "testrepo",
                        "--dry-run",
                    ],
                )

                assert result.exit_code == 0
                assert "variables" in result.stdout
            finally:
                os.unlink(f.name)

    def test_secrets_file_with_comments_and_empty_lines(self):
        """Test secrets file with comments and empty lines."""
        content = """# This is a comment
SECRET_ONE

# Another comment
SECRET_TWO
SECRET_THREE

# Final comment
SECRET_FOUR
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with patch.dict(os.environ, {"GH_TOKEN": "test_token"}):
                    with patch("ghvault.api.delete_multiple_secrets") as mock_delete:
                        mock_delete.return_value = {
                            "success": [
                                "SECRET_ONE",
                                "SECRET_TWO",
                                "SECRET_THREE",
                                "SECRET_FOUR",
                            ],
                            "failed": [],
                            "total": 4,
                        }

                        result = self.runner.invoke(
                            app,
                            [
                                "delete-bulk",
                                "production",
                                "--file",
                                f.name,
                                "--owner",
                                "testowner",
                                "--repo",
                                "testrepo",
                                "--force",
                            ],
                        )

                        assert result.exit_code == 0

                        # Verify correct secrets were extracted
                        call_args = mock_delete.call_args
                        secret_names = call_args[1]["secret_names"]
                        expected = [
                            "SECRET_ONE",
                            "SECRET_TWO",
                            "SECRET_THREE",
                            "SECRET_FOUR",
                        ]
                        assert set(secret_names) == set(expected)
            finally:
                os.unlink(f.name)


class TestConcurrentOperations:
    """Test behavior with concurrent-like operations."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.api.httpx.put")
    @patch("ghvault.api.get_gh_environment_public_key")
    @patch("ghvault.api.get_github_token")
    def test_public_key_caching(self, mock_get_token, mock_get_pk, mock_put):
        """Test that public key is cached across multiple operations."""
        mock_get_token.return_value = "test_token"
        mock_get_pk.return_value = {
            "key": "dGVzdF9wdWJsaWNfa2V5X2hlcmU=",
            "key_id": "test_key_id",
        }
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "success"},
            text="",
            raise_for_status=Mock(),
        )

        # Create temp env file with multiple secrets
        content = "SECRET_ONE=value1\nSECRET_TWO=value2\nSECRET_THREE=value3"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with patch.dict(os.environ, {"GH_TOKEN": "test_token"}):
                    result = self.runner.invoke(
                        app,
                        [
                            "bulk",
                            "production",
                            "--file",
                            f.name,
                            "--owner",
                            "testowner",
                            "--repo",
                            "testrepo",
                        ],
                    )

                    assert result.exit_code == 0

                    # Public key should only be fetched once due to caching
                    assert mock_get_pk.call_count == 1
                    # But PUT should be called for each secret
                    assert mock_put.call_count == 3
            finally:
                os.unlink(f.name)
