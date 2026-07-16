"""
Tests for OAuth 2.0 client-credentials authentication
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import urllib.error
import urllib.parse
from blaaiz.client import BlaaizAPIClient, ALL_SCOPES
from blaaiz.blaaiz import Blaaiz
from blaaiz.error import BlaaizError


def _mock_token_response(mock_urlopen, body, status=200):
    """Configure a mocked urlopen to return a token JSON body."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(body).encode("utf-8")
    mock_response.status = status
    mock_urlopen.return_value.__enter__.return_value = mock_response
    return mock_response


class TestOAuthConstruction(unittest.TestCase):
    """Credential selection and validation."""

    def test_oauth_when_both_credentials_present(self):
        client = BlaaizAPIClient(client_id="cid", client_secret="csecret")
        self.assertTrue(client.use_oauth)
        self.assertNotIn("x-blaaiz-api-key", client.default_headers)

    def test_legacy_when_only_api_key_present(self):
        client = BlaaizAPIClient("test-api-key")
        self.assertFalse(client.use_oauth)
        self.assertEqual(client.default_headers["x-blaaiz-api-key"], "test-api-key")

    def test_oauth_preferred_when_both_oauth_and_api_key_present(self):
        client = BlaaizAPIClient(api_key="test-api-key", client_id="cid", client_secret="csecret")
        self.assertTrue(client.use_oauth)
        self.assertNotIn("x-blaaiz-api-key", client.default_headers)

    def test_missing_client_secret_is_not_oauth(self):
        client = BlaaizAPIClient(api_key="test-api-key", client_id="cid")
        self.assertFalse(client.use_oauth)

    def test_raises_when_no_credentials(self):
        with self.assertRaises(BlaaizError) as context:
            BlaaizAPIClient()
        self.assertIn("Authentication required", str(context.exception))
        self.assertIsNone(context.exception.status)
        self.assertIsNone(context.exception.code)

    def test_raises_when_only_partial_oauth_and_no_api_key(self):
        with self.assertRaises(BlaaizError):
            BlaaizAPIClient(client_id="cid")

    def test_blaaiz_class_accepts_oauth(self):
        sdk = Blaaiz(client_id="cid", client_secret="csecret")
        self.assertTrue(sdk.client.use_oauth)

    def test_blaaiz_class_backward_compatible_positional_api_key(self):
        sdk = Blaaiz("test-api-key")
        self.assertFalse(sdk.client.use_oauth)
        self.assertEqual(sdk.client.api_key, "test-api-key")


class TestOAuthScope(unittest.TestCase):
    """Default / explicit scope handling."""

    def test_default_scope_is_all_scopes_space_joined(self):
        client = BlaaizAPIClient(client_id="cid", client_secret="csecret")
        self.assertEqual(client.oauth_scope, " ".join(ALL_SCOPES))
        self.assertEqual(len(ALL_SCOPES), 21)

    def test_explicit_empty_scope_is_preserved(self):
        client = BlaaizAPIClient(client_id="cid", client_secret="csecret", oauth_scope="")
        self.assertEqual(client.oauth_scope, "")

    def test_custom_scope_is_preserved(self):
        client = BlaaizAPIClient(
            client_id="cid", client_secret="csecret", oauth_scope="wallet:read"
        )
        self.assertEqual(client.oauth_scope, "wallet:read")

    def test_all_scopes_order(self):
        self.assertEqual(ALL_SCOPES[0], "wallet:read")
        self.assertEqual(ALL_SCOPES[-1], "rates:read")


class TestOAuthTokenFetch(unittest.TestCase):
    """Token fetch, caching, refresh and header behavior."""

    def setUp(self):
        self.client = BlaaizAPIClient(client_id="cid", client_secret="csecret")

    @patch("blaaiz.client.time.time")
    @patch("urllib.request.urlopen")
    def test_token_fetch_and_bearer_header(self, mock_urlopen, mock_time):
        mock_time.return_value = 1000
        _mock_token_response(mock_urlopen, {"access_token": "tok-abc", "expires_in": 3600})

        headers = self.client.get_auth_headers()

        self.assertEqual(headers, {"Authorization": "Bearer tok-abc"})
        # Token expiry = now + expires_in - 60
        self.assertEqual(self.client._token_expires_at, 1000 + 3600 - 60)

        # Verify request shape
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api-dev.blaaiz.com/oauth/token")
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.headers["Content-type"], "application/x-www-form-urlencoded")
        sent = urllib.parse.parse_qs(req.data.decode("utf-8"))
        self.assertEqual(sent["grant_type"], ["client_credentials"])
        self.assertEqual(sent["client_id"], ["cid"])
        self.assertEqual(sent["client_secret"], ["csecret"])
        self.assertEqual(sent["scope"], [" ".join(ALL_SCOPES)])

    @patch("blaaiz.client.time.time")
    @patch("urllib.request.urlopen")
    def test_token_default_expires_in_when_missing(self, mock_urlopen, mock_time):
        mock_time.return_value = 500
        _mock_token_response(mock_urlopen, {"access_token": "tok-abc"})

        self.client.get_oauth_token()
        self.assertEqual(self.client._token_expires_at, 500 + 900 - 60)

    @patch("blaaiz.client.time.time")
    @patch("urllib.request.urlopen")
    def test_token_string_expires_in_is_coerced(self, mock_urlopen, mock_time):
        mock_time.return_value = 1000
        _mock_token_response(mock_urlopen, {"access_token": "tok-abc", "expires_in": "3600"})

        first = self.client.get_oauth_token()
        self.assertEqual(first, "tok-abc")
        self.assertEqual(self.client._token_expires_at, 1000 + 3600 - 60)

        # Cached and reused within the validity window (no re-fetch)
        mock_time.return_value = 2000
        second = self.client.get_oauth_token()
        self.assertEqual(second, "tok-abc")
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("blaaiz.client.time.time")
    @patch("urllib.request.urlopen")
    def test_token_is_cached_and_reused(self, mock_urlopen, mock_time):
        mock_time.return_value = 1000
        _mock_token_response(mock_urlopen, {"access_token": "tok-1", "expires_in": 3600})

        first = self.client.get_oauth_token()
        # Still within validity window
        mock_time.return_value = 2000
        second = self.client.get_oauth_token()

        self.assertEqual(first, "tok-1")
        self.assertEqual(second, "tok-1")
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("blaaiz.client.time.time")
    @patch("urllib.request.urlopen")
    def test_token_refreshed_after_expiry(self, mock_urlopen, mock_time):
        mock_time.return_value = 1000
        _mock_token_response(mock_urlopen, {"access_token": "tok-1", "expires_in": 100})

        first = self.client.get_oauth_token()
        self.assertEqual(first, "tok-1")

        # Past the buffered expiry (1000 + 100 - 60 = 1040)
        mock_time.return_value = 1041
        _mock_token_response(mock_urlopen, {"access_token": "tok-2", "expires_in": 100})
        second = self.client.get_oauth_token()

        self.assertEqual(second, "tok-2")
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("urllib.request.urlopen")
    def test_parse_error_on_missing_access_token(self, mock_urlopen):
        _mock_token_response(mock_urlopen, {"token_type": "Bearer"}, status=200)
        with self.assertRaises(BlaaizError) as context:
            self.client.get_oauth_token()
        self.assertEqual(context.exception.code, "OAUTH_PARSE_ERROR")
        self.assertEqual(context.exception.status, 200)

    @patch("urllib.request.urlopen")
    def test_parse_error_on_invalid_json(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        with self.assertRaises(BlaaizError) as context:
            self.client.get_oauth_token()
        self.assertEqual(context.exception.code, "OAUTH_PARSE_ERROR")

    @patch("urllib.request.urlopen")
    def test_http_error_uses_error_description(self, mock_urlopen):
        error_body = json.dumps(
            {"error": "invalid_client", "error_description": "Client authentication failed"}
        )
        mock_error = urllib.error.HTTPError(
            url="test", code=401, msg="Unauthorized", hdrs=None, fp=None
        )
        mock_error.read = MagicMock(return_value=error_body.encode("utf-8"))
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(BlaaizError) as context:
            self.client.get_oauth_token()
        self.assertEqual(context.exception.message, "Client authentication failed")
        self.assertEqual(context.exception.status, 401)
        self.assertEqual(context.exception.code, "invalid_client")

    @patch("urllib.request.urlopen")
    def test_http_error_falls_back_to_oauth_error(self, mock_urlopen):
        mock_error = urllib.error.HTTPError(
            url="test", code=500, msg="Server Error", hdrs=None, fp=None
        )
        mock_error.read = MagicMock(return_value=b"gateway down")
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(BlaaizError) as context:
            self.client.get_oauth_token()
        self.assertEqual(context.exception.status, 500)
        self.assertEqual(context.exception.code, "OAUTH_ERROR")

    @patch("urllib.request.urlopen")
    def test_transport_error_raises_oauth_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        with self.assertRaises(BlaaizError) as context:
            self.client.get_oauth_token()
        self.assertIsNone(context.exception.status)
        self.assertEqual(context.exception.code, "OAUTH_ERROR")
        self.assertIn("OAuth token request failed", context.exception.message)

    @patch("urllib.request.urlopen")
    def test_token_request_uses_configured_base_url(self, mock_urlopen):
        client = BlaaizAPIClient(
            client_id="cid", client_secret="csecret", base_url="https://api.blaaiz.com"
        )
        _mock_token_response(mock_urlopen, {"access_token": "tok", "expires_in": 3600})
        client.get_oauth_token()
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.blaaiz.com/oauth/token")


class TestLegacyAuthHeaders(unittest.TestCase):
    """Legacy API-key header behavior."""

    def test_legacy_auth_headers(self):
        client = BlaaizAPIClient("test-api-key")
        self.assertEqual(client.get_auth_headers(), {"x-blaaiz-api-key": "test-api-key"})


if __name__ == "__main__":
    unittest.main()
