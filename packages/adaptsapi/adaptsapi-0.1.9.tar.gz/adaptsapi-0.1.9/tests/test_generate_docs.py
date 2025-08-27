import pytest
import requests
import os
from unittest.mock import patch, Mock
from adaptsapi.generate_docs import (
    post,
    _validate_payload,
    _populate_metadata,
    PayloadValidationError,
)


class TestPayloadValidation:
    """Test payload validation functionality"""

    def test_valid_payload(self):
        """Test that a valid payload passes validation"""
        payload = {
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
        # Should not raise any exception
        _validate_payload(payload)

    def test_missing_required_field(self):
        """Test validation fails when required fields are missing"""
        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            # Missing repo_object
        }
        with pytest.raises(
            PayloadValidationError, match="Missing required field: 'repo_object'"
        ):
            _validate_payload(payload)

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format"""
        payload = {
            "email_address": "invalid-email",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }
        with pytest.raises(
            PayloadValidationError, match="Invalid email address format"
        ):
            _validate_payload(payload)

    def test_missing_repo_required_fields(self):
        """Test validation fails when repo_object is missing required fields"""
        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                # Missing other required fields
            },
        }
        with pytest.raises(
            PayloadValidationError, match="Missing repo_object.repository_url"
        ):
            _validate_payload(payload)

    def test_invalid_field_types(self):
        """Test validation fails with wrong field types"""
        payload = {
            "email_address": "test@example.com",
            "user_name": 123,  # Should be string
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }
        with pytest.raises(
            PayloadValidationError, match="Field 'user_name' must be of type str"
        ):
            _validate_payload(payload)

    def test_optional_fields_validation(self):
        """Test that optional fields are validated when present"""
        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
                "is_private": "not_a_boolean",  # Should be boolean
            },
        }
        with pytest.raises(
            PayloadValidationError, match="repo_object.is_private must be bool"
        ):
            _validate_payload(payload)


class TestMetadataPopulation:
    """Test metadata population functionality"""

    def test_metadata_population(self):
        """Test that metadata is correctly populated"""
        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }

        _populate_metadata(payload)

        # Check that metadata was added
        assert "metadata" in payload
        assert payload["metadata"]["created_by"] == "test@example.com"
        assert payload["metadata"]["updated_by"] == "test@example.com"
        assert "created_on" in payload["metadata"]
        assert "updated_on" in payload["metadata"]

        # Check that action and other fields were added
        assert payload["action"] == "code_to_wiki"
        assert "request_id" in payload
        assert payload["request_type"] == "code_to_wiki"
        assert payload["status"] == "pending"

        # Check wiki_object was created
        assert "wiki_object" in payload
        assert payload["wiki_object"]["wiki_name"] == "test-repo"
        assert payload["wiki_object"]["wiki_source"] == "github"

    def test_existing_wiki_object_preserved(self):
        """Test that existing wiki_object is preserved and extended"""
        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
            "wiki": {"wiki_name": "custom-name", "wiki_url": "https://custom-wiki.com"},
        }

        _populate_metadata(payload)

        # Check that existing wiki fields are preserved
        assert payload["wiki_object"]["wiki_name"] == "custom-name"
        assert payload["wiki_object"]["wiki_url"] == "https://custom-wiki.com"
        assert payload["wiki_object"]["wiki_source"] == "github"


class TestPostFunction:
    """Test the main post function"""

    @patch("adaptsapi.generate_docs.requests.post")
    def test_successful_post(self, mock_post):
        """Test successful API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "id": "123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }

        response = post("https://api.example.com/test", "test-token", payload)

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL and headers
        assert call_args[0][0] == "https://api.example.com/test"
        assert call_args[1]["headers"]["x-api-key"] == "test-token"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

        # Check that payload was processed (metadata added)
        sent_payload = call_args[1]["json"]
        assert "metadata" in sent_payload
        assert "request_id" in sent_payload
        assert sent_payload["action"] == "code_to_wiki"

        # Check timeout
        assert call_args[1]["timeout"] == 30

    @patch("adaptsapi.generate_docs.requests.post")
    def test_custom_timeout(self, mock_post):
        """Test post function with custom timeout"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }

        post("https://api.example.com/test", "test-token", payload, timeout=60)

        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 60

    def test_invalid_payload_raises_error(self):
        """Test that invalid payload raises PayloadValidationError"""
        invalid_payload = {
            "email_address": "invalid-email",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }

        with pytest.raises(PayloadValidationError):
            post("https://api.example.com/test", "test-token", invalid_payload)

    @patch("adaptsapi.generate_docs.requests.post")
    def test_request_exception_handling(self, mock_post):
        """Test that request exceptions are properly raised"""
        mock_post.side_effect = requests.RequestException("Network error")

        payload = {
            "email_address": "test@example.com",
            "user_name": "testuser",
            "repo_object": {
                "repository_name": "test-repo",
                "source": "github",
                "repository_url": "https://github.com/test/test-repo",
                "branch": "main",
                "size": "100",
                "language": "Python",
            },
        }

        with pytest.raises(requests.RequestException):
            post("https://api.example.com/test", "test-token", payload)


class TestIntegration:
    """Integration tests that can be run against real API (optional)"""

    @pytest.mark.integration
    def test_real_api_call(self):
        """Test against real API endpoint (requires ADAPTS_API_KEY env var)"""
        auth_token = os.getenv("ADAPTS_API_KEY")
        if not auth_token:
            pytest.skip("ADAPTS_API_KEY environment variable not set")

        payload = {
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

        try:
            response = post(
                "https://ycdwnfjohl.execute-api.us-east-1.amazonaws.com/prod/generate_wiki_docs",
                auth_token,
                payload,
            )
            response.raise_for_status()
            result = response.json()
            print("API Response:", result)
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.fail(f"API call failed: {e}")


if __name__ == "__main__":
    # Run the test that was in the original file
    auth_token = os.getenv("ADAPTS_API_KEY")
    if auth_token:
        payload = {
            "email_address": "sheel@adapts.ai",
            "user_name": "sheel",
            "repo_object": {
                "repository_name": "kotlin-tree-sitter",
                "source": "github",
                "repository_url": "https://github.com/tree-sitter/kotlin-tree-sitter",
                "branch": "master",
                "size": "100",
                "language": "Kotlin",
                "is_private": False,
                "git_provider_type": "github",
                "refresh_token": "1234567890",
            },
        }

        try:
            resp = post(
                "https://ycdwnfjohl.execute-api.us-east-1.amazonaws.com/prod/generate_wiki_docs",
                auth_token,
                payload,
            )
            resp.raise_for_status()
            print(resp.json())
        except PayloadValidationError as e:
            print("Invalid payload:", e)
        except requests.RequestException as e:
            print("Request failed:", e)
    else:
        print("ADAPTS_API_KEY environment variable not set")
