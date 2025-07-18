"""
Blaaiz SDK Main Class
"""

from typing import Dict, Any, Optional
from .client import BlaaizAPIClient
from .error import BlaaizError
from .services import (
    CustomerService,
    CollectionService,
    PayoutService,
    WalletService,
    VirtualBankAccountService,
    TransactionService,
    BankService,
    CurrencyService,
    FeesService,
    FileService,
    WebhookService,
)


class Blaaiz:
    """
    Main Blaaiz SDK class that provides access to all services.

    This class follows the method chaining pattern similar to the Node.js SDK,
    allowing you to access services like: blaaiz.customers.create(...)
    """

    def __init__(
        self, api_key: str, base_url: str = "https://api-dev.blaaiz.com", timeout: int = 30
    ):
        """
        Initialize the Blaaiz SDK.

        Args:
            api_key: Your Blaaiz API key
            base_url: Base URL for the API (defaults to dev environment)
            timeout: Request timeout in seconds
        """
        self.client = BlaaizAPIClient(api_key, base_url, timeout)

        # Initialize all services with method chaining
        self.customers = CustomerService(self.client)
        self.collections = CollectionService(self.client)
        self.payouts = PayoutService(self.client)
        self.wallets = WalletService(self.client)
        self.virtual_bank_accounts = VirtualBankAccountService(self.client)
        self.transactions = TransactionService(self.client)
        self.banks = BankService(self.client)
        self.currencies = CurrencyService(self.client)
        self.fees = FeesService(self.client)
        self.files = FileService(self.client)
        self.webhooks = WebhookService(self.client)

    def test_connection(self) -> bool:
        """
        Test the connection to the Blaaiz API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.currencies.list()
            return True
        except Exception:
            return False

    def create_complete_payout(self, payout_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete payout workflow (customer + fee calculation + payout).

        Args:
            payout_config: Configuration containing:
                - customer_data: Optional customer data (if customer needs to be created)
                - payout_data: Payout information

        Returns:
            Dictionary containing customer_id, payout result, and fee breakdown
        """
        customer_data = payout_config.get("customer_data")
        payout_data = payout_config.get("payout_data")

        if not payout_data:
            raise ValueError("payout_data is required")

        try:
            # Create customer if needed
            customer_id = payout_data.get("customer_id")
            if not customer_id and customer_data:
                customer_result = self.customers.create(customer_data)
                customer_id = customer_result["data"]["data"]["id"]

            # Get fee breakdown
            fee_breakdown = self.fees.get_breakdown(
                {
                    "from_currency_id": payout_data["from_currency_id"],
                    "to_currency_id": payout_data["to_currency_id"],
                    "from_amount": payout_data["from_amount"],
                }
            )

            # Create payout
            payout_data_with_customer = {**payout_data, "customer_id": customer_id}
            payout_result = self.payouts.initiate(payout_data_with_customer)

            return {
                "customer_id": customer_id,
                "payout": payout_result["data"],
                "fees": fee_breakdown["data"],
            }

        except Exception as e:
            if isinstance(e, BlaaizError):
                raise BlaaizError(f"Complete payout failed: {e.message}", e.status, e.code)
            else:
                raise BlaaizError(f"Complete payout failed: {str(e)}")

    def create_complete_collection(self, collection_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete collection workflow (customer + VBA + collection).

        Args:
            collection_config: Configuration containing:
                - customer_data: Optional customer data (if customer needs to be created)
                - collection_data: Collection information
                - create_vba: Whether to create a virtual bank account

        Returns:
            Dictionary containing customer_id, collection result, and optional VBA data
        """
        customer_data = collection_config.get("customer_data")
        collection_data = collection_config.get("collection_data")
        create_vba = collection_config.get("create_vba", False)

        if not collection_data:
            raise ValueError("collection_data is required")

        try:
            # Create customer if needed
            customer_id = collection_data.get("customer_id")
            if not customer_id and customer_data:
                customer_result = self.customers.create(customer_data)
                customer_id = customer_result["data"]["data"]["id"]

            # Create virtual bank account if requested
            vba_data = None
            if create_vba:
                account_name = "Customer Account"
                if customer_data:
                    account_name = f"{customer_data['first_name']} {customer_data['last_name']}"

                vba_result = self.virtual_bank_accounts.create(
                    {"wallet_id": collection_data["wallet_id"], "account_name": account_name}
                )
                vba_data = vba_result["data"]

            # Create collection
            collection_data_with_customer = {**collection_data, "customer_id": customer_id}
            collection_result = self.collections.initiate(collection_data_with_customer)

            return {
                "customer_id": customer_id,
                "collection": collection_result["data"],
                "virtual_account": vba_data,
            }

        except Exception as e:
            if isinstance(e, BlaaizError):
                raise BlaaizError(f"Complete collection failed: {e.message}", e.status, e.code)
            else:
                raise BlaaizError(f"Complete collection failed: {str(e)}")

    # Convenience methods for common operations
    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """Get customer by ID."""
        return self.customers.get(customer_id)

    def get_transaction_by_id(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction by ID."""
        return self.transactions.get(transaction_id)

    def get_wallet_by_id(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet by ID."""
        return self.wallets.get(wallet_id)

    def get_all_currencies(self) -> Dict[str, Any]:
        """Get all supported currencies."""
        return self.currencies.list()

    def get_all_banks(self) -> Dict[str, Any]:
        """Get all supported banks."""
        return self.banks.list()

    def calculate_fees(
        self, from_currency_id: str, to_currency_id: str, from_amount: float
    ) -> Dict[str, Any]:
        """Calculate fees for a transaction."""
        return self.fees.get_breakdown(
            {
                "from_currency_id": from_currency_id,
                "to_currency_id": to_currency_id,
                "from_amount": from_amount,
            }
        )

    # Context manager support
    def __enter__(self) -> "Blaaiz":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    def __repr__(self) -> str:
        return f"Blaaiz(base_url='{self.client.base_url}')"
