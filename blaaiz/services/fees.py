"""
Fees Service
"""

from typing import Dict, Any


class FeesService:
    """Service for managing fees."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def get_breakdown(self, fee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fee breakdown.

        Args:
            fee_data: Fee calculation data containing:
                - from_currency_id: Source currency ID
                - to_currency_id: Target currency ID
                - from_amount: Amount to send (OR to_amount)
                - to_amount: Amount recipient should receive (OR from_amount)

        Returns:
            API response containing fee breakdown
        """
        required_fields = ["from_currency_id", "to_currency_id"]

        for field in required_fields:
            if field not in fee_data or not fee_data[field]:
                raise ValueError(f"{field} is required")

        # Either from_amount or to_amount must be provided
        if not fee_data.get("from_amount") and not fee_data.get("to_amount"):
            raise ValueError("Either from_amount or to_amount is required")

        return self.client.make_request("POST", "/api/external/fees/breakdown", fee_data)
