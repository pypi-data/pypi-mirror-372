import unittest
from unittest import mock
import json
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ekacare import EkaCareClient
from ekacare.utils.exceptions import EkaCareAPIError, EkaCareAuthError


class TestEkaCareClient(unittest.TestCase):
    """Tests for the EkaCare SDK client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = EkaCareClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            base_url="https://api.test.eka.care"
        )
        # Create a mock for the session to avoid actual API calls
        self.client.session = mock.MagicMock()
        
        # Mock successful response
        self.mock_response = mock.MagicMock()
        self.mock_response.ok = True
        self.mock_response.status_code = 200
        self.mock_response.headers = {'Content-Type': 'application/json'}
        self.mock_response.json.return_value = {"success": True}
        self.mock_response.text = json.dumps({"success": True})
        
        # Set the mock response as the return value for request methods
        self.client.session.request.return_value = self.mock_response

    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.client_id, "test_client_id")
        self.assertEqual(self.client.client_secret, "test_client_secret")
        self.assertEqual(self.client.base_url, "https://api.test.eka.care")
        
    def test_request_method(self):
        """Test the request method."""
        # Test a simple GET request
        result = self.client.request(
            method="GET",
            endpoint="/test/endpoint",
            auth_required=False
        )
        
        # Check the result
        self.assertEqual(result, {"success": True})
        
        # Verify the request was made correctly
        self.client.session.request.assert_called_once_with(
            method="GET",
            url="https://api.test.eka.care/test/endpoint",
            params=None,
            data=None,
            json=None,
            headers={"client-id": "test_client_id"},
            files=None
        )
        
    def test_auth_required_request(self):
        """Test request with auth token."""
        # Mock the access token
        self.client._access_token = "test_access_token"
        
        # Make a request that requires auth
        self.client.request(
            method="GET",
            endpoint="/auth/endpoint"
        )
        
        # Verify the Authorization header was included
        self.client.session.request.assert_called_once()
        call_kwargs = self.client.session.request.call_args[1]
        self.assertEqual(
            call_kwargs["headers"],
            {
                "Authorization": "Bearer test_access_token",
                "client-id": "test_client_id"
            }
        )
        
    def test_auth_error_handling(self):
        """Test handling of authentication errors."""
        # Mock a 401 response
        error_response = mock.MagicMock()
        error_response.ok = False
        error_response.status_code = 401
        error_response.text = "Unauthorized"
        
        self.client.session.request.return_value = error_response
        
        # Attempt to make a request that will fail with a 401
        with self.assertRaises(EkaCareAuthError):
            self.client.request(
                method="GET",
                endpoint="/secured/endpoint"
            )
            
    def test_api_error_handling(self):
        """Test handling of general API errors."""
        # Mock a 400 response
        error_response = mock.MagicMock()
        error_response.ok = False
        error_response.status_code = 400
        error_response.text = "Bad Request"
        
        self.client.session.request.return_value = error_response
        
        # Attempt to make a request that will fail with a 400
        with self.assertRaises(EkaCareAPIError):
            self.client.request(
                method="POST",
                endpoint="/some/endpoint",
                json={"invalid": "data"}
            )
            
    @mock.patch('ekacare.auth.auth.Auth.login')
    def test_access_token_auto_fetch(self, mock_login):
        """Test automatic fetching of access token."""
        # Mock the auth.login method
        mock_login.return_value = {"access_token": "new_access_token"}
        
        # Clear any existing access token
        self.client._access_token = None
        
        # Access the token property, which should trigger login
        token = self.client.access_token
        
        # Verify login was called and token was set
        mock_login.assert_called_once()
        self.assertEqual(token, "new_access_token")
        self.assertEqual(self.client._access_token, "new_access_token")
        
    def test_records_upload_document(self):
        """Test the records.upload_document method."""
        # Mock the get_authorization and session.post methods
        self.client.records.get_authorization = mock.MagicMock(return_value={
            "batch_response": [
                {
                    "document_id": "test_document_id",
                    "forms": [
                        {
                            "url": "https://upload.url",
                            "fields": {"field1": "value1"}
                        }
                    ]
                }
            ]
        })
        
        upload_response = mock.MagicMock()
        upload_response.ok = True
        self.client.session.post.return_value = upload_response
        
        # Create a temporary test file
        test_file = "test_file.pdf"
        with open(test_file, "w") as f:
            f.write("test content")
        
        try:
            # Call the upload_document method
            result = self.client.records.upload_document(
                file_path=test_file,
                document_type="ps",
                tags=["test"]
            )
            
            # Verify the result
            self.assertEqual(result, {"document_id": "test_document_id"})
            
            # Verify get_authorization was called with correct parameters
            self.client.records.get_authorization.assert_called_once()
            args = self.client.records.get_authorization.call_args[0][0]
            self.assertEqual(args[0]["dt"], "ps")
            self.assertEqual(args[0]["tg"], ["test"])
            
            # Verify session.post was called for the file upload
            self.client.session.post.assert_called_once()
            args = self.client.session.post.call_args[1]
            self.assertEqual(args["url"], "https://upload.url")
            self.assertEqual(args["data"], {"field1": "value1"})
            self.assertIn("files", args)
        finally:
            # Clean up the test file
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':
    unittest.main()