"""
Blaaiz API Client
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Union
from .error import BlaaizError


class BlaaizAPIClient:
    """HTTP client for interacting with the Blaaiz API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api-dev.blaaiz.com", timeout: int = 30):
        """
        Initialize the Blaaiz API client.
        
        Args:
            api_key: Your Blaaiz API key
            base_url: Base URL for the API (defaults to dev environment)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_headers = {
            'x-blaaiz-api-key': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Blaaiz-Python-SDK/1.0.0'
        }
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None
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
        
        # Prepare headers
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare data
        request_data = None
        if data and method.upper() != 'GET':
            if isinstance(data, str):
                request_data = data.encode('utf-8')
            else:
                request_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            url,
            data=request_data,
            headers=request_headers,
            method=method.upper()
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                
                try:
                    parsed_data = json.loads(response_data)
                except json.JSONDecodeError:
                    parsed_data = response_data
                
                return {
                    'data': parsed_data,
                    'status': response.status,
                    'headers': dict(response.headers)
                }
                
        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                message = error_data.get('message', 'API request failed')
                code = error_data.get('code', 'HTTP_ERROR')
            except (json.JSONDecodeError, AttributeError):
                message = f"HTTP {e.code} error"
                code = 'HTTP_ERROR'
            
            raise BlaaizError(message, e.code, code)
            
        except urllib.error.URLError as e:
            raise BlaaizError(f"Request failed: {str(e)}", None, 'REQUEST_ERROR')
        
        except Exception as e:
            raise BlaaizError(f"Unexpected error: {str(e)}", None, 'UNEXPECTED_ERROR')