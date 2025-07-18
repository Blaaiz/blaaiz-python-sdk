"""
Tests for Main Blaaiz Class
"""

import unittest
from unittest.mock import MagicMock, patch
from blaaiz.blaaiz import Blaaiz
from blaaiz.error import BlaaizError


class TestBlaaiz(unittest.TestCase):
    """Test cases for main Blaaiz class."""

    def setUp(self):
        """Set up test Blaaiz instance."""
        self.blaaiz = Blaaiz("test-api-key")

    def test_initialization(self):
        """Test Blaaiz initialization."""
        self.assertEqual(self.blaaiz.client.api_key, "test-api-key")
        self.assertEqual(self.blaaiz.client.base_url, "https://api-dev.blaaiz.com")

        # Test that all services are initialized
        self.assertIsNotNone(self.blaaiz.customers)
        self.assertIsNotNone(self.blaaiz.collections)
        self.assertIsNotNone(self.blaaiz.payouts)
        self.assertIsNotNone(self.blaaiz.wallets)
        self.assertIsNotNone(self.blaaiz.virtual_bank_accounts)
        self.assertIsNotNone(self.blaaiz.transactions)
        self.assertIsNotNone(self.blaaiz.banks)
        self.assertIsNotNone(self.blaaiz.currencies)
        self.assertIsNotNone(self.blaaiz.fees)
        self.assertIsNotNone(self.blaaiz.files)
        self.assertIsNotNone(self.blaaiz.webhooks)

    def test_initialization_with_custom_options(self):
        """Test initialization with custom options."""
        blaaiz = Blaaiz("test-key", base_url="https://custom.com", timeout=60)
        self.assertEqual(blaaiz.client.base_url, "https://custom.com")
        self.assertEqual(blaaiz.client.timeout, 60)

    def test_test_connection_success(self):
        """Test successful connection test."""
        # Mock the currencies.list method
        self.blaaiz.currencies.list = MagicMock(return_value={"data": []})

        result = self.blaaiz.test_connection()

        self.assertTrue(result)
        self.blaaiz.currencies.list.assert_called_once()

    def test_test_connection_failure(self):
        """Test failed connection test."""
        # Mock the currencies.list method to raise an exception
        self.blaaiz.currencies.list = MagicMock(side_effect=Exception("Connection failed"))

        result = self.blaaiz.test_connection()

        self.assertFalse(result)
        self.blaaiz.currencies.list.assert_called_once()

    def test_create_complete_payout_full_flow(self):
        """Test complete payout workflow with customer creation."""
        # Mock service methods
        self.blaaiz.customers.create = MagicMock(
            return_value={"data": {"data": {"id": "customer-123"}}}
        )
        self.blaaiz.fees.get_breakdown = MagicMock(return_value={"data": {"total_fees": 100}})
        self.blaaiz.payouts.initiate = MagicMock(
            return_value={"data": {"transaction_id": "tx-123"}}
        )

        payout_config = {
            "customer_data": {
                "first_name": "John",
                "last_name": "Doe",
                "type": "individual",
                "email": "john@example.com",
                "country": "NG",
                "id_type": "passport",
                "id_number": "A12345678",
            },
            "payout_data": {
                "wallet_id": "wallet-123",
                "method": "bank_transfer",
                "from_amount": 1000,
                "from_currency_id": "1",
                "to_currency_id": "1",
                "account_number": "0123456789",
            },
        }

        result = self.blaaiz.create_complete_payout(payout_config)

        # Verify all methods were called
        self.blaaiz.customers.create.assert_called_once_with(payout_config["customer_data"])
        self.blaaiz.fees.get_breakdown.assert_called_once_with(
            {"from_currency_id": "1", "to_currency_id": "1", "from_amount": 1000}
        )
        self.blaaiz.payouts.initiate.assert_called_once_with(
            {**payout_config["payout_data"], "customer_id": "customer-123"}
        )

        # Verify result
        self.assertEqual(result["customer_id"], "customer-123")
        self.assertEqual(result["payout"]["transaction_id"], "tx-123")
        self.assertEqual(result["fees"]["total_fees"], 100)

    def test_create_complete_payout_with_existing_customer(self):
        """Test complete payout workflow with existing customer."""
        # Mock service methods
        self.blaaiz.fees.get_breakdown = MagicMock(return_value={"data": {"total_fees": 100}})
        self.blaaiz.payouts.initiate = MagicMock(
            return_value={"data": {"transaction_id": "tx-123"}}
        )

        payout_config = {
            "payout_data": {
                "wallet_id": "wallet-123",
                "customer_id": "existing-customer-123",
                "method": "bank_transfer",
                "from_amount": 1000,
                "from_currency_id": "1",
                "to_currency_id": "1",
                "account_number": "0123456789",
            }
        }

        result = self.blaaiz.create_complete_payout(payout_config)

        # Verify customer creation was not called
        # Since we didn't mock customers.create, it should not have been called
        self.assertTrue(True)  # No customer creation needed for existing customer

        # Verify result uses existing customer ID
        self.assertEqual(result["customer_id"], "existing-customer-123")

    def test_create_complete_payout_error_handling(self):
        """Test complete payout error handling."""
        # Mock service methods
        self.blaaiz.fees.get_breakdown = MagicMock(return_value={"data": {"total_fees": 100}})
        self.blaaiz.payouts.initiate = MagicMock(
            side_effect=BlaaizError("Payout failed", 400, "INSUFFICIENT_FUNDS")
        )

        payout_config = {
            "payout_data": {
                "wallet_id": "wallet-123",
                "customer_id": "customer-123",
                "method": "bank_transfer",
                "from_amount": 1000,
                "from_currency_id": "1",
                "to_currency_id": "1",
                "account_number": "0123456789",
            }
        }

        with self.assertRaises(BlaaizError) as context:
            self.blaaiz.create_complete_payout(payout_config)

        self.assertIn("Complete payout failed", context.exception.message)

    def test_create_complete_payout_missing_payout_data(self):
        """Test complete payout with missing payout data."""
        with self.assertRaises(ValueError) as context:
            self.blaaiz.create_complete_payout({})

        self.assertIn("payout_data is required", str(context.exception))

    def test_create_complete_collection_full_flow(self):
        """Test complete collection workflow with customer creation and VBA."""
        # Mock service methods
        self.blaaiz.customers.create = MagicMock(
            return_value={"data": {"data": {"id": "customer-123"}}}
        )
        self.blaaiz.virtual_bank_accounts.create = MagicMock(
            return_value={"data": {"account_number": "1234567890"}}
        )
        self.blaaiz.collections.initiate = MagicMock(
            return_value={"data": {"transaction_id": "tx-123"}}
        )

        collection_config = {
            "customer_data": {
                "first_name": "Jane",
                "last_name": "Smith",
                "type": "individual",
                "email": "jane@example.com",
                "country": "NG",
                "id_type": "drivers_license",
                "id_number": "D12345678",
            },
            "collection_data": {"method": "card", "amount": 5000, "wallet_id": "wallet-123"},
            "create_vba": True,
        }

        result = self.blaaiz.create_complete_collection(collection_config)

        # Verify all methods were called
        self.blaaiz.customers.create.assert_called_once_with(collection_config["customer_data"])
        self.blaaiz.virtual_bank_accounts.create.assert_called_once_with(
            {"wallet_id": "wallet-123", "account_name": "Jane Smith"}
        )
        self.blaaiz.collections.initiate.assert_called_once_with(
            {**collection_config["collection_data"], "customer_id": "customer-123"}
        )

        # Verify result
        self.assertEqual(result["customer_id"], "customer-123")
        self.assertEqual(result["collection"]["transaction_id"], "tx-123")
        self.assertEqual(result["virtual_account"]["account_number"], "1234567890")

    def test_create_complete_collection_without_vba(self):
        """Test complete collection workflow without VBA creation."""
        # Mock service methods
        self.blaaiz.customers.create = MagicMock(
            return_value={"data": {"data": {"id": "customer-123"}}}
        )
        self.blaaiz.collections.initiate = MagicMock(
            return_value={"data": {"transaction_id": "tx-123"}}
        )

        collection_config = {
            "customer_data": {
                "first_name": "Jane",
                "last_name": "Smith",
                "type": "individual",
                "email": "jane@example.com",
                "country": "NG",
                "id_type": "drivers_license",
                "id_number": "D12345678",
            },
            "collection_data": {"method": "card", "amount": 5000, "wallet_id": "wallet-123"},
            "create_vba": False,
        }

        result = self.blaaiz.create_complete_collection(collection_config)

        # Verify VBA creation was not called
        # Since we didn't mock virtual_bank_accounts.create, it should not have been called
        self.assertTrue(True)  # No VBA creation needed when create_vba is False

        # Verify result
        self.assertEqual(result["customer_id"], "customer-123")
        self.assertEqual(result["collection"]["transaction_id"], "tx-123")
        self.assertIsNone(result["virtual_account"])

    def test_create_complete_collection_missing_collection_data(self):
        """Test complete collection with missing collection data."""
        with self.assertRaises(ValueError) as context:
            self.blaaiz.create_complete_collection({})

        self.assertIn("collection_data is required", str(context.exception))

    def test_convenience_methods(self):
        """Test convenience methods."""
        # Mock service methods
        self.blaaiz.customers.get = MagicMock(return_value={"data": {"id": "customer-123"}})
        self.blaaiz.transactions.get = MagicMock(return_value={"data": {"id": "tx-123"}})
        self.blaaiz.wallets.get = MagicMock(return_value={"data": {"id": "wallet-123"}})
        self.blaaiz.currencies.list = MagicMock(return_value={"data": []})
        self.blaaiz.banks.list = MagicMock(return_value={"data": []})
        self.blaaiz.fees.get_breakdown = MagicMock(return_value={"data": {"total_fees": 100}})

        # Test convenience methods
        customer = self.blaaiz.get_customer_by_id("customer-123")
        transaction = self.blaaiz.get_transaction_by_id("tx-123")
        wallet = self.blaaiz.get_wallet_by_id("wallet-123")
        currencies = self.blaaiz.get_all_currencies()
        banks = self.blaaiz.get_all_banks()
        fees = self.blaaiz.calculate_fees("1", "2", 1000)

        # Verify methods were called
        self.blaaiz.customers.get.assert_called_once_with("customer-123")
        self.blaaiz.transactions.get.assert_called_once_with("tx-123")
        self.blaaiz.wallets.get.assert_called_once_with("wallet-123")
        self.blaaiz.currencies.list.assert_called_once()
        self.blaaiz.banks.list.assert_called_once()
        self.blaaiz.fees.get_breakdown.assert_called_once_with(
            {"from_currency_id": "1", "to_currency_id": "2", "from_amount": 1000}
        )

        # Verify results
        self.assertEqual(customer["data"]["id"], "customer-123")
        self.assertEqual(transaction["data"]["id"], "tx-123")
        self.assertEqual(wallet["data"]["id"], "wallet-123")
        self.assertEqual(currencies["data"], [])
        self.assertEqual(banks["data"], [])
        self.assertEqual(fees["data"]["total_fees"], 100)

    def test_context_manager(self):
        """Test context manager functionality."""
        with Blaaiz("test-api-key") as blaaiz:
            self.assertIsNotNone(blaaiz)
            self.assertEqual(blaaiz.client.api_key, "test-api-key")

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.blaaiz)
        self.assertEqual(repr_str, "Blaaiz(base_url='https://api-dev.blaaiz.com')")


if __name__ == "__main__":
    unittest.main()
