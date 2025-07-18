"""
Tests for Blaaiz API Client
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import urllib.error
from blaaiz.client import BlaaizAPIClient
from blaaiz.error import BlaaizError


class TestBlaaizAPIClient(unittest.TestCase):
    """Test cases for BlaaizAPIClient."""

    def setUp(self):
        """Set up test client."""
        self.client = BlaaizAPIClient("test-api-key")

    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, "test-api-key")
        self.assertEqual(self.client.base_url, "https://api-dev.blaaiz.com")
        self.assertEqual(self.client.timeout, 30)
        self.assertIn("x-blaaiz-api-key", self.client.default_headers)

    def test_initialization_with_options(self):
        """Test client initialization with custom options."""
        client = BlaaizAPIClient("test-key", base_url="https://custom.com", timeout=60)
        self.assertEqual(client.base_url, "https://custom.com")
        self.assertEqual(client.timeout, 60)

    def test_initialization_without_api_key(self):
        """Test client initialization without API key raises error."""
        with self.assertRaises(ValueError) as context:
            BlaaizAPIClient("")
        self.assertIn("API key is required", str(context.exception))

    @patch("urllib.request.urlopen")
    def test_successful_request(self, mock_urlopen):
        """Test successful API request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"success": True}).encode("utf-8")
        mock_response.status = 200
        mock_response.headers = {"content-type": "application/json"}

        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.make_request("GET", "/test")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["data"]["success"], True)

    @patch("urllib.request.urlopen")
    def test_request_with_data(self, mock_urlopen):
        """Test API request with data."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"received": True}).encode("utf-8")
        mock_response.status = 201
        mock_response.headers = {}

        mock_urlopen.return_value.__enter__.return_value = mock_response

        test_data = {"name": "test"}
        result = self.client.make_request("POST", "/test", test_data)

        self.assertEqual(result["status"], 201)
        self.assertEqual(result["data"]["received"], True)

    @patch("urllib.request.urlopen")
    def test_http_error(self, mock_urlopen):
        """Test HTTP error handling."""
        error_response = json.dumps({"message": "Not found", "code": "NOT_FOUND"})

        # Create a mock HTTPError with a proper read method
        mock_error = urllib.error.HTTPError(
            url="test", code=404, msg="Not Found", hdrs=None, fp=None
        )
        mock_error.read = MagicMock(return_value=error_response.encode("utf-8"))
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(BlaaizError) as context:
            self.client.make_request("GET", "/test")

        self.assertEqual(context.exception.status, 404)
        self.assertEqual(context.exception.code, "NOT_FOUND")

    @patch("urllib.request.urlopen")
    def test_url_error(self, mock_urlopen):
        """Test URL error handling."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection failed")

        with self.assertRaises(BlaaizError) as context:
            self.client.make_request("GET", "/test")

        self.assertEqual(context.exception.code, "REQUEST_ERROR")
        self.assertIn("Connection failed", context.exception.message)

    @patch("urllib.request.urlopen")
    def test_json_decode_error(self, mock_urlopen):
        """Test JSON decode error handling."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid json"
        mock_response.status = 200
        mock_response.headers = {}

        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.make_request("GET", "/test")

        # Should return raw response when JSON parsing fails
        self.assertEqual(result["data"], "invalid json")


if __name__ == "__main__":
    unittest.main()
