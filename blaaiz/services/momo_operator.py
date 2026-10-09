"""
Mobile Money Operator Service
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


class MomoOperatorService:
    """Service for listing mobile money operators."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def list(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List mobile money operators.

        Args:
            filters: Optional query parameters. Supported keys are
                ``currency_id`` (the destination currency ID) and ``country_id``.

        Returns:
            API response containing list of mobile money operators
        """
        endpoint = "/api/external/momo-operator"
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
