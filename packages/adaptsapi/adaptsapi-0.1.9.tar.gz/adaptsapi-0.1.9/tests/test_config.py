import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from pathlib import Path
from adaptsapi.config import (
    load_token,
    load_default_endpoint,
    ConfigError,
    _ensure_config_dir_and_write,
)


class TestTokenLoading:
    """Test token loading functionality"""

    @patch("adaptsapi.config.os.getenv")
    def test_load_token_from_env(self, mock_getenv):
        """Test loading token from environment variable"""
        mock_getenv.return_value = "env-token"

        token = load_token()
        assert token == "env-token"
        mock_getenv.assert_called_once_with("ADAPTS_API_TOKEN")

    @patch("adaptsapi.config.os.getenv")
    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_token_from_config_file(self, mock_config_path, mock_getenv):
        """Test loading token from config.json file"""
        mock_getenv.return_value = None  # No env var

        # Mock config file exists and contains token
        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = '{"token": "file-token"}'

        token = load_token()
        assert token == "file-token"

    @patch("adaptsapi.config.os.getenv")
    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_token_from_config_file_missing_token(
        self, mock_config_path, mock_getenv
    ):
        """Test loading token when config file exists but has no token"""
        mock_getenv.return_value = None

        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = '{"other_field": "value"}'

        # Should fall through to interactive prompt
        with patch("adaptsapi.config.getpass.getpass") as mock_getpass:
            mock_getpass.return_value = "interactive-token"
            with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
                token = load_token()

        assert token == "interactive-token"
        mock_write.assert_called_once()

    @patch("adaptsapi.config.os.getenv")
    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_token_invalid_json_in_config(self, mock_config_path, mock_getenv):
        """Test loading token when config file has invalid JSON"""
        mock_getenv.return_value = None

        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = "invalid json"

        # Should fall through to interactive prompt
        with patch("adaptsapi.config.getpass.getpass") as mock_getpass:
            mock_getpass.return_value = "interactive-token"
            with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
                token = load_token()

        assert token == "interactive-token"
        mock_write.assert_called_once()

    @patch("adaptsapi.config.os.getenv")
    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_token_no_config_file(self, mock_config_path, mock_getenv):
        """Test loading token when no config file exists"""
        mock_getenv.return_value = None
        mock_config_path.exists.return_value = False

        # Should fall through to interactive prompt
        with patch("adaptsapi.config.getpass.getpass") as mock_getpass:
            mock_getpass.return_value = "interactive-token"
            with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
                token = load_token()

        assert token == "interactive-token"
        mock_write.assert_called_once()

    @patch("adaptsapi.config.os.getenv")
    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_token_empty_interactive_input(self, mock_config_path, mock_getenv):
        """Test loading token when interactive input is empty"""
        mock_getenv.return_value = None
        mock_config_path.exists.return_value = False

        with patch("adaptsapi.config.getpass.getpass") as mock_getpass:
            mock_getpass.return_value = ""  # Empty input

            with pytest.raises(ConfigError, match="No token provided"):
                load_token()

    @patch("adaptsapi.config.os.getenv")
    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_token_saves_to_config_file(self, mock_config_path, mock_getenv):
        """Test that interactive token is saved to config file"""
        mock_getenv.return_value = None
        mock_config_path.exists.return_value = False

        with patch("adaptsapi.config.getpass.getpass") as mock_getpass:
            mock_getpass.return_value = "new-token"
            with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
                with patch("builtins.print") as mock_print:
                    token = load_token()

        assert token == "new-token"
        # The actual call includes indentation, so we need to check the content
        mock_write.assert_called_once()
        call_args = mock_write.call_args[0][0]
        config_data = json.loads(call_args)
        assert config_data["token"] == "new-token"
        mock_print.assert_called_once()


class TestEndpointLoading:
    """Test endpoint loading functionality"""

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_default_endpoint_exists(self, mock_config_path):
        """Test loading endpoint when config file exists and has endpoint"""
        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = (
            '{"endpoint": "https://api.example.com"}'
        )

        endpoint = load_default_endpoint()
        assert endpoint == "https://api.example.com"

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_default_endpoint_missing_endpoint(self, mock_config_path):
        """Test loading endpoint when config file exists but has no endpoint"""
        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = '{"token": "test-token"}'

        endpoint = load_default_endpoint()
        assert endpoint is None

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_default_endpoint_invalid_json(self, mock_config_path):
        """Test loading endpoint when config file has invalid JSON"""
        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = "invalid json"

        endpoint = load_default_endpoint()
        assert endpoint is None

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_load_default_endpoint_no_file(self, mock_config_path):
        """Test loading endpoint when no config file exists"""
        mock_config_path.exists.return_value = False

        endpoint = load_default_endpoint()
        assert endpoint is None


class TestConfigFileWriting:
    """Test configuration file writing functionality"""

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_ensure_config_dir_and_write_new_file(self, mock_config_path):
        """Test writing to a new config file"""
        mock_config_path.exists.return_value = False

        with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
            _ensure_config_dir_and_write({"token": "new-token"})

        mock_write.assert_called_once()
        call_args = mock_write.call_args[0][0]
        config_data = json.loads(call_args)
        assert config_data["token"] == "new-token"

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_ensure_config_dir_and_write_merge_existing(self, mock_config_path):
        """Test merging with existing config file"""
        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = (
            '{"token": "old-token", "endpoint": "https://old.api.com"}'
        )

        with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
            _ensure_config_dir_and_write({"token": "new-token"})

        # Should merge existing config with new values
        expected_config = {"token": "new-token", "endpoint": "https://old.api.com"}
        mock_write.assert_called_once_with(json.dumps(expected_config, indent=2))

    @patch("adaptsapi.config.CONFIG_PATH")
    def test_ensure_config_dir_and_write_merge_invalid_existing(self, mock_config_path):
        """Test merging when existing config file has invalid JSON"""
        mock_config_path.exists.return_value = True
        mock_config_path.read_text.return_value = "invalid json"

        with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
            _ensure_config_dir_and_write({"token": "new-token"})

        # Should use only the new config
        mock_write.assert_called_once()
        call_args = mock_write.call_args[0][0]
        config_data = json.loads(call_args)
        assert config_data["token"] == "new-token"


class TestConfigIntegration:
    """Integration tests for config functionality"""

    def test_token_loading_priority(self):
        """Test that environment variable takes priority over config file"""
        with patch("adaptsapi.config.os.getenv") as mock_getenv:
            mock_getenv.return_value = "env-token"

            with patch("adaptsapi.config.CONFIG_PATH") as mock_config_path:
                mock_config_path.exists.return_value = True
                mock_config_path.read_text.return_value = '{"token": "file-token"}'

                token = load_token()
                assert token == "env-token"  # Environment should take priority

    def test_config_file_structure(self):
        """Test that config file is written with proper structure"""
        with patch("adaptsapi.config.CONFIG_PATH") as mock_config_path:
            mock_config_path.exists.return_value = False

            with patch("adaptsapi.config.CONFIG_PATH.write_text") as mock_write:
                _ensure_config_dir_and_write(
                    {"token": "test-token", "endpoint": "https://api.example.com"}
                )

            # Verify the JSON structure
            call_args = mock_write.call_args[0][0]
            config_data = json.loads(call_args)
            assert config_data["token"] == "test-token"
            assert config_data["endpoint"] == "https://api.example.com"

    def test_real_config_file_creation(self):
        """Test creating a real config file in a temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()

            try:
                # Change to temp directory
                os.chdir(temp_dir)

                # Temporarily patch CONFIG_PATH to point to our temp directory
                with patch(
                    "adaptsapi.config.CONFIG_PATH", Path(temp_dir) / "config.json"
                ):
                    # Test writing config
                    _ensure_config_dir_and_write(
                        {"token": "temp-token", "endpoint": "https://temp.api.com"}
                    )

                # Verify file was created
                config_file = Path(temp_dir) / "config.json"
                assert config_file.exists()

                # Verify content
                with open(config_file, "r") as f:
                    config_data = json.load(f)
                    assert config_data["token"] == "temp-token"
                    assert config_data["endpoint"] == "https://temp.api.com"

            finally:
                # Restore original directory
                os.chdir(original_cwd)
