"""
Blaaiz API Client
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Union, List
from .error import BlaaizError

# Full set of OAuth scopes requested by default, in a fixed order (kept in sync
# with the Laravel and Node.js SDKs). Sent space-joined as the `scope` param.
ALL_SCOPES: List[str] = [
    "wallet:read",
    "currency:read",
    "bank:read",
    "customer:read",
    "customer:write",
    "beneficiary:read",
    "virtual-account:read",
    "virtual-account:create",
    "virtual-account:close",
    "collection:create",
    "collection:crypto:create",
    "collection:interac:accept",
    "payout:create",
    "swap:create",
    "transaction:read",
    "fees:read",
    "file:upload",
    "webhook:read",
    "webhook:write",
    "webhook:replay",
    "rates:read",
]


class BlaaizAPIClient:
    """HTTP client for interacting with the Blaaiz API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api-dev.blaaiz.com",
        timeout: int = 30,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        oauth_scope: Optional[str] = None,
    ):
        """
        Initialize the Blaaiz API client.

        Authenticate with either OAuth 2.0 client credentials (``client_id`` and
        ``client_secret``) or a legacy ``api_key``. When both are provided, OAuth
        is used.

        Args:
            api_key: Your Blaaiz API key (legacy authentication)
            base_url: Base URL for the API (defaults to dev environment)
            timeout: Request timeout in seconds
            client_id: OAuth client ID
            client_secret: OAuth client secret
            oauth_scope: Space-separated OAuth scopes. When None, the full
                default scope set is requested. An explicit empty string is
                sent as-is.
        """
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""
        self.oauth_scope = " ".join(ALL_SCOPES) if oauth_scope is None else oauth_scope
        self.api_key = api_key or ""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.use_oauth = bool(self.client_id) and bool(self.client_secret)

        if not self.use_oauth and not self.api_key:
            raise BlaaizError(
                "Authentication required: provide either client_id and client_secret "
                "for OAuth, or api_key for legacy authentication"
            )

        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[int] = None

        self.default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Blaaiz-Python-SDK/1.1.1",
        }
        if not self.use_oauth:
            self.default_headers["x-blaaiz-api-key"] = self.api_key

    def get_oauth_token(self) -> str:
        """
        Fetch and cache an OAuth access token using the client-credentials grant.

        A cached token is reused until 60 seconds before its expiry.

        Returns:
            The bearer access token

        Raises:
            BlaaizError: If the token request fails or the response is invalid
        """
        now = int(time.time())
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            return self._access_token

        url = f"{self.base_url}/oauth/token"
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.oauth_scope,
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode("utf-8")
                status = response.status

        except urllib.error.HTTPError as e:
            error_data = None
            try:
                error_data = json.loads(e.read().decode("utf-8"))
            except (json.JSONDecodeError, AttributeError, ValueError):
                error_data = None

            if isinstance(error_data, dict):
                message = (
                    error_data.get("error_description")
                    or error_data.get("message")
                    or f"OAuth token request failed: {str(e)}"
                )
                code = error_data.get("error") or "OAUTH_ERROR"
            else:
                message = f"OAuth token request failed: {str(e)}"
                code = "OAUTH_ERROR"

            raise BlaaizError(message, e.code, code)

        except urllib.error.URLError as e:
            raise BlaaizError(f"OAuth token request failed: {str(e)}", None, "OAUTH_ERROR")

        try:
            parsed = json.loads(response_data)
        except json.JSONDecodeError:
            parsed = None

        if not isinstance(parsed, dict) or not parsed.get("access_token"):
            raise BlaaizError("Failed to parse OAuth token response", status, "OAUTH_PARSE_ERROR")

        access_token = parsed["access_token"]
        self._access_token = access_token
        expires_in = parsed.get("expires_in")
        if expires_in is None:
            expires_in = 900
        self._token_expires_at = int(time.time()) + expires_in - 60
        return access_token

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Resolve authentication headers for a request.

        OAuth mode returns a bearer ``Authorization`` header (refreshing the
        token cache as needed); legacy mode returns the API key header.
        """
        if self.use_oauth:
            return {"Authorization": f"Bearer {self.get_oauth_token()}"}
        return {"x-blaaiz-api-key": self.api_key}

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Blaaiz API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request payload
            headers: Additional headers

        Returns:
            Dictionary containing response data, status, and headers

        Raises:
            BlaaizError: If the request fails
        """
        # Prepare URL
        url = f"{self.base_url}{endpoint}"

        # Prepare headers (auth headers resolved per request, caller headers win)
        request_headers = self.default_headers.copy()
        request_headers.update(self.get_auth_headers())
        if headers:
            request_headers.update(headers)

        # Prepare data
        request_data = None
        if data and method.upper() != "GET":
            if isinstance(data, str):
                request_data = data.encode("utf-8")
            else:
                request_data = json.dumps(data).encode("utf-8")

        # Create request
        req = urllib.request.Request(
            url, data=request_data, headers=request_headers, method=method.upper()
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode("utf-8")

                try:
                    parsed_data = json.loads(response_data)
                except json.JSONDecodeError:
                    parsed_data = response_data

                return {
                    "data": parsed_data,
                    "status": response.status,
                    "headers": dict(response.headers),
                }

        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode("utf-8"))
                message = error_data.get("message", "API request failed")
                code = error_data.get("code", "HTTP_ERROR")
            except (json.JSONDecodeError, AttributeError):
                message = f"HTTP {e.code} error"
                code = "HTTP_ERROR"

            raise BlaaizError(message, e.code, code)

        except urllib.error.URLError as e:
            raise BlaaizError(f"Request failed: {str(e)}", None, "REQUEST_ERROR")

        except Exception as e:
            raise BlaaizError(f"Unexpected error: {str(e)}", None, "UNEXPECTED_ERROR")
