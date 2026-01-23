"""
Payout Service
"""

from typing import Dict, Any, List


class PayoutService:
    """Service for managing payouts."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def _validate_required_fields(self, data: Dict[str, Any], fields: List[str]) -> None:
        """Validate that required fields are present and non-empty."""
        for field in fields:
            if field not in data or not data[field]:
                raise ValueError(f"{field} is required")

    def _validate_bank_transfer_fields(self, payout_data: Dict[str, Any], to_currency: str) -> None:
        """Validate bank transfer specific fields based on currency."""
        # NGN bank transfers require bank_id and account_number
        if to_currency == "NGN":
            self._validate_required_fields(payout_data, ["bank_id", "account_number"])
        # GBP bank transfers require sort_code and account_number
        elif to_currency == "GBP":
            self._validate_required_fields(
                payout_data, ["sort_code", "account_number", "account_name"]
            )
        # EUR bank transfers require IBAN and BIC code
        elif to_currency == "EUR":
            self._validate_required_fields(payout_data, ["iban", "bic_code", "account_name"])

    def _validate_ach_wire_fields(self, payout_data: Dict[str, Any], method: str) -> None:
        """Validate ACH/Wire specific fields."""
        self._validate_required_fields(
            payout_data,
            [
                "type",
                "account_number",
                "account_name",
                "account_type",
                "bank_name",
                "routing_number",
            ],
        )

        if method == "wire":
            self._validate_required_fields(payout_data, ["swift_code"])

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
            "customer_id",
            "method",
            "from_currency_id",
            "to_currency_id",
        ]

        self._validate_required_fields(payout_data, required_fields)

        # Either from_amount or to_amount must be provided
        if not payout_data.get("from_amount") and not payout_data.get("to_amount"):
            raise ValueError("Either from_amount or to_amount is required")

        method = payout_data["method"]
        to_currency: str = payout_data["to_currency_id"]

        # Method-specific validations
        if method == "bank_transfer":
            self._validate_bank_transfer_fields(payout_data, to_currency)
        elif method == "interac":
            self._validate_required_fields(
                payout_data, ["email", "interac_first_name", "interac_last_name"]
            )
        elif method in ["ach", "wire"]:
            self._validate_ach_wire_fields(payout_data, method)
        elif method == "crypto":
            self._validate_required_fields(
                payout_data, ["wallet_address", "wallet_token", "wallet_network"]
            )

        return self.client.make_request("POST", "/api/external/payout", payout_data)
