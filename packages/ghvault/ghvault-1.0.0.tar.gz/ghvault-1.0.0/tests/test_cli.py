# tests/test_cli.py
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest  # type: ignore
from typer.testing import CliRunner

from ghvault.cli import app, ensure_github_token


class TestEnsureGitHubToken:
    """Test the ensure_github_token function."""

    def test_ensure_github_token_already_set(self, mock_env_vars):
        """Test when token is already in environment."""
        # Should not prompt or validate since token exists
        ensure_github_token()
        # No exception should be raised

    @patch("ghvault.cli.typer.prompt")
    @patch("ghvault.cli.validate_github_token")
    @patch("ghvault.cli.set_github_token")
    def test_ensure_github_token_prompt_success(self, mock_set_token, mock_validate, mock_prompt):
        """Test successful token prompt and validation."""
        mock_prompt.return_value = "new_token_123"
        mock_validate.return_value = True

        with patch.dict(os.environ, {}, clear=True):
            ensure_github_token()

        mock_prompt.assert_called_once()
        mock_validate.assert_called_once_with("new_token_123")
        mock_set_token.assert_called_once_with("new_token_123")
        assert os.environ.get("GH_TOKEN") == "new_token_123"

    @patch("ghvault.cli.typer.prompt")
    @patch("ghvault.cli.validate_github_token")
    def test_ensure_github_token_empty_token(self, mock_validate, mock_prompt):
        """Test when empty token is provided."""
        mock_prompt.return_value = "   "  # Empty/whitespace token

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                ensure_github_token()

    @patch("ghvault.cli.typer.prompt")
    @patch("ghvault.cli.validate_github_token")
    def test_ensure_github_token_invalid_token(self, mock_validate, mock_prompt):
        """Test when invalid token is provided."""
        mock_prompt.return_value = "invalid_token"
        mock_validate.return_value = False

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                ensure_github_token()


class TestSetCommand:
    """Test the 'set' CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.cli.create_or_update_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_set_command_success(self, mock_ensure_token, mock_create_secret):
        """Test successful secret setting."""
        mock_create_secret.return_value = {"status": "success"}

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
        mock_ensure_token.assert_called_once()
        mock_create_secret.assert_called_once_with("testowner", "testrepo", "production", "TEST_SECRET", "secret_value")

    @patch("ghvault.cli.create_or_update_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_set_command_with_env_vars(self, mock_ensure_token, mock_create_secret):
        """Test secret setting using environment variables for repo info."""
        mock_create_secret.return_value = {"status": "success"}

        with patch.dict(os.environ, {"GH_OWNER": "envowner", "GH_REPO": "envrepo"}):
            result = self.runner.invoke(app, ["set", "staging", "ENV_SECRET", "env_value"])

        assert result.exit_code == 0
        mock_create_secret.assert_called_once_with("envowner", "envrepo", "staging", "ENV_SECRET", "env_value")

    def test_set_command_missing_repo_info(self):
        """Test error when repository information is missing."""
        result = self.runner.invoke(app, ["set", "production", "TEST_SECRET", "secret_value"])

        assert result.exit_code == 1
        assert "Missing repo info" in result.stdout

    @patch("ghvault.cli.ensure_github_token")
    def test_set_command_no_value(self, mock_ensure_token):
        """Test error when no value is provided."""
        result = self.runner.invoke(
            app,
            [
                "set",
                "production",
                "TEST_SECRET",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
            ],
        )

        assert result.exit_code == 1
        assert "You must provide either a value or a --file" in result.stdout

    @patch("ghvault.cli.create_or_update_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_set_command_with_file(self, mock_ensure_token, mock_create_secret):
        """Test setting secret from file."""
        mock_create_secret.return_value = {"status": "success"}

        # Create temporary file with secret value
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write('{"api_key": "secret_from_file"}')
            f.flush()

            try:
                result = self.runner.invoke(
                    app,
                    [
                        "set",
                        "production",
                        "JSON_SECRET",
                        "--file",
                        f.name,
                        "--owner",
                        "testowner",
                        "--repo",
                        "testrepo",
                    ],
                )

                assert result.exit_code == 0
                mock_create_secret.assert_called_once()
                # Should be called with JSON string
                args = mock_create_secret.call_args[0]
                assert '"api_key": "secret_from_file"' in args[4]
            finally:
                os.unlink(f.name)

    @patch("ghvault.cli.create_or_update_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_set_command_api_failure(self, mock_ensure_token, mock_create_secret):
        """Test handling of API failure."""
        mock_create_secret.side_effect = RuntimeError("API Error")

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

        assert result.exit_code == 1
        assert "Failed to set secret" in result.stdout


class TestBulkCommand:
    """Test the 'bulk' CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.cli.write_env_to_github")
    @patch("ghvault.cli.ensure_github_token")
    def test_bulk_command_success(self, mock_ensure_token, mock_write_env, temp_env_file):
        """Test successful bulk upload."""
        mock_write_env.return_value = {
            "success": ["SECRET_ONE", "SECRET_TWO"],
            "failed": [],
            "total": 2,
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
            ],
        )

        assert result.exit_code == 0
        assert "All 2 secrets uploaded successfully" in result.stdout
        mock_ensure_token.assert_called_once()
        mock_write_env.assert_called_once()

    @patch("ghvault.cli.write_env_to_github")
    def test_bulk_command_dry_run(self, mock_write_env, temp_env_file):
        """Test dry run mode."""
        mock_write_env.return_value = {
            "dry_run": True,
            "variables": ["SECRET_ONE", "SECRET_TWO"],
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
        assert "Dry run completed" in result.stdout
        assert "Found 2 variables" in result.stdout

    def test_bulk_command_file_not_found(self):
        """Test error when .env file doesn't exist."""
        result = self.runner.invoke(
            app,
            [
                "bulk",
                "production",
                "--file",
                "/nonexistent/file.env",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
            ],
        )

        assert result.exit_code == 1
        assert ".env file not found" in result.stdout

    @patch("ghvault.cli.write_env_to_github")
    @patch("ghvault.cli.ensure_github_token")
    def test_bulk_command_partial_failure(self, mock_ensure_token, mock_write_env, temp_env_file):
        """Test bulk upload with some failures."""
        mock_write_env.return_value = {
            "success": ["SECRET_ONE"],
            "failed": [{"name": "SECRET_TWO", "error": "Permission denied"}],
            "total": 2,
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
            ],
        )

        assert result.exit_code == 1
        assert "Upload completed with 1 failures" in result.stdout


class TestListCommand:
    """Test the 'list' CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.cli.list_environment_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_list_command_success(self, mock_ensure_token, mock_list_secrets):
        """Test successful secret listing."""
        mock_list_secrets.return_value = ["SECRET_ONE", "SECRET_TWO", "SECRET_THREE"]

        result = self.runner.invoke(app, ["list", "production", "--owner", "testowner", "--repo", "testrepo"])

        assert result.exit_code == 0
        assert "Found 3 secrets" in result.stdout
        assert "SECRET_ONE" in result.stdout
        assert "SECRET_TWO" in result.stdout
        assert "SECRET_THREE" in result.stdout
        mock_ensure_token.assert_called_once()
        mock_list_secrets.assert_called_once_with("testowner", "testrepo", "production")

    @patch("ghvault.cli.list_environment_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_list_command_empty(self, mock_ensure_token, mock_list_secrets):
        """Test listing when no secrets exist."""
        mock_list_secrets.return_value = []

        result = self.runner.invoke(app, ["list", "production", "--owner", "testowner", "--repo", "testrepo"])

        assert result.exit_code == 0
        assert "No secrets found" in result.stdout

    @patch("ghvault.cli.list_environment_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_list_command_failure(self, mock_ensure_token, mock_list_secrets):
        """Test handling of listing failure."""
        mock_list_secrets.side_effect = RuntimeError("Environment not found")

        result = self.runner.invoke(app, ["list", "production", "--owner", "testowner", "--repo", "testrepo"])

        assert result.exit_code == 1
        assert "Failed to list secrets" in result.stdout


class TestDeleteCommand:
    """Test the 'delete' CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.cli.delete_environment_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_command_success_with_force(self, mock_ensure_token, mock_delete_secret):
        """Test successful secret deletion with --force flag."""
        mock_delete_secret.return_value = True

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
        mock_ensure_token.assert_called_once()
        mock_delete_secret.assert_called_once_with("testowner", "testrepo", "production", "TEST_SECRET")

    @patch("ghvault.cli.delete_environment_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_command_with_confirmation(self, mock_ensure_token, mock_delete_secret):
        """Test secret deletion with user confirmation."""
        mock_delete_secret.return_value = True

        # Simulate user confirming deletion
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
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        assert "Secret 'TEST_SECRET' deleted" in result.stdout

    @patch("ghvault.cli.ensure_github_token")
    def test_delete_command_cancelled(self, mock_ensure_token):
        """Test deletion cancelled by user."""
        # Simulate user cancelling deletion
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
            ],
            input="n\n",
        )

        assert result.exit_code == 1
        assert "Deletion cancelled" in result.stdout

    @patch("ghvault.cli.delete_environment_secret")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_command_failure(self, mock_ensure_token, mock_delete_secret):
        """Test handling of deletion failure."""
        mock_delete_secret.side_effect = RuntimeError("Secret not found")

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

        assert result.exit_code == 1
        assert "Failed to delete secret" in result.stdout


class TestDeleteBulkCommand:
    """Test the 'delete-bulk' CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("ghvault.cli.delete_multiple_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_bulk_command_with_file(self, mock_ensure_token, mock_delete_multiple, temp_secrets_file):
        """Test bulk deletion using secrets file."""
        mock_delete_multiple.return_value = {
            "success": ["SECRET_ONE", "SECRET_TWO", "SECRET_THREE", "SECRET_FOUR"],
            "failed": [],
            "total": 4,
        }

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
        assert "All 4 secrets deleted successfully" in result.stdout
        mock_ensure_token.assert_called_once()

        # Verify the correct secrets were passed
        call_args = mock_delete_multiple.call_args
        secret_names = call_args[1]["secret_names"]
        expected_secrets = ["SECRET_ONE", "SECRET_TWO", "SECRET_THREE", "SECRET_FOUR"]
        assert set(secret_names) == set(expected_secrets)

    @patch("ghvault.cli.delete_multiple_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_bulk_command_with_names(self, mock_ensure_token, mock_delete_multiple):
        """Test bulk deletion using comma-separated names."""
        mock_delete_multiple.return_value = {
            "success": ["SECRET_A", "SECRET_B"],
            "failed": [],
            "total": 2,
        }

        result = self.runner.invoke(
            app,
            [
                "delete-bulk",
                "production",
                "--names",
                "SECRET_A,SECRET_B",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
                "--force",
            ],
        )

        assert result.exit_code == 0
        assert "All 2 secrets deleted successfully" in result.stdout

        # Verify the correct secrets were passed
        call_args = mock_delete_multiple.call_args
        secret_names = call_args[1]["secret_names"]
        assert set(secret_names) == {"SECRET_A", "SECRET_B"}

    def test_delete_bulk_command_no_input(self):
        """Test error when neither file nor names are provided."""
        result = self.runner.invoke(
            app,
            ["delete-bulk", "production", "--owner", "testowner", "--repo", "testrepo"],
        )

        assert result.exit_code == 1
        assert "You must provide either --file or --names" in result.stdout

    def test_delete_bulk_command_file_not_found(self):
        """Test error when secrets file doesn't exist."""
        result = self.runner.invoke(
            app,
            [
                "delete-bulk",
                "production",
                "--file",
                "/nonexistent/secrets.txt",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
            ],
        )

        assert result.exit_code == 1
        assert "File not found" in result.stdout

    @patch("ghvault.cli.delete_multiple_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_bulk_command_with_confirmation(self, mock_ensure_token, mock_delete_multiple):
        """Test bulk deletion with user confirmation."""
        mock_delete_multiple.return_value = {
            "success": ["SECRET_A"],
            "failed": [],
            "total": 1,
        }

        # Simulate user confirming deletion
        result = self.runner.invoke(
            app,
            [
                "delete-bulk",
                "production",
                "--names",
                "SECRET_A",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        assert "All 1 secrets deleted successfully" in result.stdout

    @patch("ghvault.cli.ensure_github_token")
    def test_delete_bulk_command_cancelled(self, mock_ensure_token):
        """Test bulk deletion cancelled by user."""
        # Simulate user cancelling deletion
        result = self.runner.invoke(
            app,
            [
                "delete-bulk",
                "production",
                "--names",
                "SECRET_A",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
            ],
            input="n\n",
        )

        assert result.exit_code == 1
        assert "Deletion cancelled" in result.stdout

    @patch("ghvault.cli.delete_multiple_secrets")
    @patch("ghvault.cli.ensure_github_token")
    def test_delete_bulk_command_partial_failure(self, mock_ensure_token, mock_delete_multiple):
        """Test bulk deletion with some failures."""
        mock_delete_multiple.return_value = {
            "success": ["SECRET_A"],
            "failed": [{"name": "SECRET_B", "error": "Not found"}],
            "total": 2,
        }

        result = self.runner.invoke(
            app,
            [
                "delete-bulk",
                "production",
                "--names",
                "SECRET_A,SECRET_B",
                "--owner",
                "testowner",
                "--repo",
                "testrepo",
                "--force",
            ],
        )

        assert result.exit_code == 1
        assert "Deletion completed with 1 failures" in result.stdout


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_app_help(self):
        """Test that help command works."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "ghvault - Manage GitHub environment secrets securely" in result.stdout

    def test_command_help(self):
        """Test help for individual commands."""
        commands = ["set", "bulk", "list", "delete", "delete-bulk"]

        for command in commands:
            result = self.runner.invoke(app, [command, "--help"])
            assert result.exit_code == 0
            assert command in result.stdout.lower() or "help" in result.stdout.lower()
