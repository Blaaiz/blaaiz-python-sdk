"""
Payout Service
"""

from typing import Dict, Any


class PayoutService:
    """Service for managing payouts."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def initiate(self, payout_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a payout.

        Args:
            payout_data: Payout information

        Returns:
            API response containing payout data
        """
        required_fields = [
            "wallet_id",
            "method",
            "from_amount",
            "from_currency_id",
            "to_currency_id",
        ]

        for field in required_fields:
            if field not in payout_data or not payout_data[field]:
                raise ValueError(f"{field} is required")

        if payout_data["method"] == "bank_transfer" and not payout_data.get("account_number"):
            raise ValueError("account_number is required for bank_transfer method")

        if payout_data["method"] == "interac":
            interac_fields = ["email", "interac_first_name", "interac_last_name"]
            for field in interac_fields:
                if field not in payout_data or not payout_data[field]:
                    raise ValueError(f"{field} is required for interac method")

        return self.client.make_request("POST", "/api/external/payout", payout_data)
