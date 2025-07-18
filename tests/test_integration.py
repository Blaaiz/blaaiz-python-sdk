"""
Integration Tests for Blaaiz Python SDK

These tests require a valid API key and should be run against a test environment.
Set BLAAIZ_API_KEY environment variable to run these tests.
"""

import unittest
import os
from blaaiz import Blaaiz, BlaaizError


class TestBlaaizIntegration(unittest.TestCase):
    """Integration test cases for Blaaiz SDK."""

    def setUp(self):
        """Set up integration test."""
        self.api_key = os.getenv("BLAAIZ_API_KEY")
        if not self.api_key:
            self.skipTest("BLAAIZ_API_KEY environment variable not set")

        self.blaaiz = Blaaiz(self.api_key)

    def test_connection(self):
        """Test API connection."""
        is_connected = self.blaaiz.test_connection()
        self.assertTrue(is_connected, "Failed to connect to Blaaiz API")

    def test_list_currencies(self):
        """Test listing currencies."""
        try:
            currencies = self.blaaiz.currencies.list()
            self.assertIsInstance(currencies, dict)
            self.assertIn("data", currencies)
            self.assertIsInstance(currencies["data"], list)
        except BlaaizError as e:
            self.fail(f"Failed to list currencies: {e.message}")

    def test_list_banks(self):
        """Test listing banks."""
        try:
            banks = self.blaaiz.banks.list()
            self.assertIsInstance(banks, dict)
            self.assertIn("data", banks)
            self.assertIsInstance(banks["data"], list)
        except BlaaizError as e:
            self.fail(f"Failed to list banks: {e.message}")

    def test_list_wallets(self):
        """Test listing wallets."""
        try:
            wallets = self.blaaiz.wallets.list()
            self.assertIsInstance(wallets, dict)
            self.assertIn("data", wallets)
            self.assertIsInstance(wallets["data"], list)
        except BlaaizError as e:
            self.fail(f"Failed to list wallets: {e.message}")

    def test_create_customer(self):
        """Test creating a customer."""
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "type": "individual",
            "email": f"john.doe.{os.urandom(4).hex()}@example.com",  # Unique email
            "country": "NG",
            "id_type": "passport",
            "id_number": f"A{os.urandom(4).hex().upper()}",  # Unique ID
        }

        try:
            customer = self.blaaiz.customers.create(customer_data)
            self.assertIsInstance(customer, dict)
            self.assertIn("data", customer)
            self.assertIn("data", customer["data"])
            self.assertIn("id", customer["data"]["data"])

            # Test getting the created customer
            customer_id = customer["data"]["data"]["id"]
            retrieved_customer = self.blaaiz.customers.get(customer_id)
            self.assertEqual(retrieved_customer["data"]["id"], customer_id)

        except BlaaizError as e:
            self.fail(f"Failed to create customer: {e.message}")

    def test_calculate_fees(self):
        """Test calculating fees."""
        try:
            fees = self.blaaiz.fees.get_breakdown(
                {
                    "from_currency_id": "1",  # Assuming NGN
                    "to_currency_id": "2",  # Assuming CAD
                    "from_amount": 100000,
                }
            )
            self.assertIsInstance(fees, dict)
            self.assertIn("data", fees)
            self.assertIn("total_fees", fees["data"])
            self.assertIsInstance(fees["data"]["total_fees"], (int, float))

        except BlaaizError as e:
            self.fail(f"Failed to calculate fees: {e.message}")

    def test_webhook_signature_verification(self):
        """Test webhook signature verification."""
        payload = '{"transaction_id": "test-123", "status": "completed"}'
        secret = "test-webhook-secret"

        # Generate a valid signature
        import hmac
        import hashlib

        valid_signature = hmac.new(
            secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Test valid signature
        is_valid = self.blaaiz.webhooks.verify_signature(payload, valid_signature, secret)
        self.assertTrue(is_valid)

        # Test invalid signature
        is_invalid = self.blaaiz.webhooks.verify_signature(payload, "invalid-signature", secret)
        self.assertFalse(is_invalid)

        # Test construct event
        event = self.blaaiz.webhooks.construct_event(payload, valid_signature, secret)
        self.assertEqual(event["transaction_id"], "test-123")
        self.assertEqual(event["status"], "completed")
        self.assertTrue(event["verified"])
        self.assertIn("timestamp", event)

    @unittest.skipIf(not os.getenv("BLAAIZ_TEST_WALLET_ID"), "BLAAIZ_TEST_WALLET_ID not set")
    def test_virtual_bank_account_creation(self):
        """Test virtual bank account creation."""
        wallet_id = os.getenv("BLAAIZ_TEST_WALLET_ID")

        try:
            vba = self.blaaiz.virtual_bank_accounts.create(
                {"wallet_id": wallet_id, "account_name": "Test Account"}
            )
            self.assertIsInstance(vba, dict)
            self.assertIn("data", vba)
            self.assertIn("account_number", vba["data"])
            self.assertIn("bank_name", vba["data"])

        except BlaaizError as e:
            self.fail(f"Failed to create virtual bank account: {e.message}")

    def test_error_handling(self):
        """Test error handling for invalid requests."""
        # Test invalid customer creation
        with self.assertRaises(ValueError):
            self.blaaiz.customers.create({})  # Missing required fields

        # Test invalid customer ID
        with self.assertRaises(BlaaizError):
            self.blaaiz.customers.get("invalid-customer-id")

        # Test invalid wallet ID
        with self.assertRaises(BlaaizError):
            self.blaaiz.wallets.get("invalid-wallet-id")


if __name__ == "__main__":
    # Only run integration tests if API key is provided
    if os.getenv("BLAAIZ_API_KEY"):
        unittest.main()
    else:
        print("Skipping integration tests - BLAAIZ_API_KEY not set")
        print("To run integration tests, set BLAAIZ_API_KEY environment variable")
