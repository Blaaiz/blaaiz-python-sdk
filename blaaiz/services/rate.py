"""
Rate Service
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


class RateService:
    """Service for retrieving exchange rates."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def list(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List exchange rates.

        Args:
            filters: Optional query parameters. Supported key ``search_term``.

        Returns:
            API response containing list of rates
        """
        endpoint = "/api/external/rate"
        if filters:
            params = {}
            for key, value in filters.items():
                if value is None:
                    continue
                if isinstance(value, bool):
                    params[key] = "true" if value else "false"
                else:
                    params[key] = value
            if params:
                endpoint = f"{endpoint}?{urlencode(params)}"
        return self.client.make_request("GET", endpoint)
