import pytest
import json
import tempfile
import os
from unittest.mock import patch, Mock, mock_open
from io import StringIO
from adaptsapi.cli import main


class TestCLIArgumentParsing:
    """Test CLI argument parsing functionality"""

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_basic_cli_with_data(self, mock_post, mock_load_token, mock_load_endpoint):
        """Test CLI with inline JSON data"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_post.return_value = mock_response

        # Test with inline JSON data
        with patch("sys.argv", ["adaptsapi", "--data", '{"test": "data"}']):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()

        # Verify post was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.example.com/test"
        assert call_args[0][1] == "test-token"
        assert call_args[0][2] == {"test": "data"}
        assert call_args[1]["timeout"] == 30  # default timeout

        # Verify output
        assert mock_stdout.getvalue().strip() == '{"status": "success"}'

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_cli_with_payload_file(
        self, mock_post, mock_load_token, mock_load_endpoint
    ):
        """Test CLI with payload file"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_post.return_value = mock_response

        # Create a temporary payload file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "data", "nested": {"value": 123}}, f)
            temp_file_path = f.name

        try:
            with patch("sys.argv", ["adaptsapi", "--payload-file", temp_file_path]):
                with patch("sys.stdout", new=StringIO()) as mock_stdout:
                    main()

            # Verify post was called with correct payload
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][2] == {"test": "data", "nested": {"value": 123}}
        finally:
            os.unlink(temp_file_path)

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_cli_with_custom_endpoint(
        self, mock_post, mock_load_token, mock_load_endpoint
    ):
        """Test CLI with custom endpoint"""
        mock_load_endpoint.return_value = None  # No default endpoint
        mock_load_token.return_value = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_post.return_value = mock_response

        with patch(
            "sys.argv",
            [
                "adaptsapi",
                "--endpoint",
                "https://custom.api.com",
                "--data",
                '{"test": "data"}',
            ],
        ):
            with patch("sys.stdout", new=StringIO()):
                main()

        # Verify custom endpoint was used
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://custom.api.com"

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_cli_with_custom_timeout(
        self, mock_post, mock_load_token, mock_load_endpoint
    ):
        """Test CLI with custom timeout"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_post.return_value = mock_response

        with patch(
            "sys.argv", ["adaptsapi", "--timeout", "60", "--data", '{"test": "data"}']
        ):
            with patch("sys.stdout", new=StringIO()):
                main()

        # Verify custom timeout was used
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 60

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    def test_cli_missing_payload(self, mock_load_token, mock_load_endpoint):
        """Test CLI error when no payload is provided"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        with patch("sys.argv", ["adaptsapi"]):
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        assert "Error: must specify --data or --payload-file" in mock_stderr.getvalue()

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_cli_api_error_response(
        self, mock_post, mock_load_token, mock_load_endpoint
    ):
        """Test CLI handling of API error responses"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "Bad Request"}'
        mock_post.return_value = mock_response

        with patch("sys.argv", ["adaptsapi", "--data", '{"test": "data"}']):
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 400
        assert 'Error 400: {"error": "Bad Request"}' in mock_stderr.getvalue()

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_cli_invalid_json_data(
        self, mock_post, mock_load_token, mock_load_endpoint
    ):
        """Test CLI error handling with invalid JSON data"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        with patch("sys.argv", ["adaptsapi", "--data", "invalid json"]):
            with pytest.raises(json.JSONDecodeError):
                main()

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    def test_cli_missing_endpoint_no_default(self, mock_load_token, mock_load_endpoint):
        """Test CLI error when no endpoint is provided and no default exists"""
        mock_load_endpoint.return_value = None
        mock_load_token.return_value = "test-token"

        with patch("sys.argv", ["adaptsapi", "--data", '{"test": "data"}']):
            with pytest.raises(SystemExit):
                main()


class TestCLIIntegration:
    """Integration tests for CLI functionality"""

    @patch("adaptsapi.cli.load_default_endpoint")
    @patch("adaptsapi.cli.load_token")
    @patch("adaptsapi.cli.post")
    def test_cli_with_real_payload_structure(
        self, mock_post, mock_load_token, mock_load_endpoint
    ):
        """Test CLI with a realistic payload structure"""
        mock_load_endpoint.return_value = "https://api.example.com/test"
        mock_load_token.return_value = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success", "request_id": "123"}'
        mock_post.return_value = mock_response

        real_payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
                "is_private": False,
                "git_provider_type": "github",
                "refresh_token": "1234567890",
            },
        }

        with patch("sys.argv", ["adaptsapi", "--data", json.dumps(real_payload)]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()

        # Verify the payload was processed correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        sent_payload = call_args[0][2]

        # Check that the original payload structure is preserved
        assert sent_payload["email_address"] == "test@example.com"
        assert sent_payload["user_name"] == "testuser"
        assert sent_payload["repo_object"]["repository_name"] == "test-repo"

        # Note: The post function adds metadata, but we're testing the CLI integration
        # The actual metadata addition is tested in test_generate_docs.py
