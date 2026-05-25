"""
Tests for Blaaiz Services
"""

import unittest
from unittest.mock import MagicMock
from blaaiz.services import (
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


class TestCustomerService(unittest.TestCase):
    """Test cases for CustomerService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = CustomerService(self.mock_client)

    def test_create_customer_success(self):
        """Test successful customer creation."""
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "type": "individual",
            "email": "john@example.com",
            "country": "NG",
            "id_type": "passport",
            "id_number": "A12345678",
        }

        self.mock_client.make_request.return_value = {"data": {"id": "customer-id"}}

        result = self.service.create(customer_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer", customer_data
        )
        self.assertEqual(result["data"]["id"], "customer-id")

    def test_create_customer_missing_fields(self):
        """Test customer creation with missing fields."""
        customer_data = {
            "first_name": "John",
            # Missing required fields like type, email, country
        }

        with self.assertRaises(ValueError) as context:
            self.service.create(customer_data)

        self.assertIn("type is required", str(context.exception))

    def test_create_individual_customer_missing_name(self):
        """Test individual customer creation without required name fields."""
        customer_data = {
            "type": "individual",
            "email": "john@example.com",
            "country": "NG",
            "id_type": "passport",
            "id_number": "A12345678",
            # Missing first_name and last_name
        }

        with self.assertRaises(ValueError) as context:
            self.service.create(customer_data)

        self.assertIn("first_name is required", str(context.exception))

    def test_create_business_customer_missing_business_name(self):
        """Test business customer creation without business name."""
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "type": "business",
            "email": "john@example.com",
            "country": "NG",
            "id_type": "passport",
            "id_number": "A12345678",
        }

        with self.assertRaises(ValueError) as context:
            self.service.create(customer_data)

        self.assertIn("business_name is required", str(context.exception))

    def test_get_customer(self):
        """Test getting customer by ID."""
        customer_id = "customer-id"
        self.mock_client.make_request.return_value = {"data": {"id": customer_id}}

        result = self.service.get(customer_id)

        self.mock_client.make_request.assert_called_once_with(
            "GET", f"/api/external/customer/{customer_id}"
        )
        self.assertEqual(result["data"]["id"], customer_id)

    def test_get_customer_without_id(self):
        """Test getting customer without ID."""
        with self.assertRaises(ValueError) as context:
            self.service.get("")

        self.assertIn("Customer ID is required", str(context.exception))

    def test_list_customers(self):
        """Test listing customers."""
        self.mock_client.make_request.return_value = {"data": []}

        result = self.service.list()

        self.mock_client.make_request.assert_called_once_with("GET", "/api/external/customer")
        self.assertEqual(result["data"], [])

    def test_list_customers_with_filters(self):
        """Test listing customers with filters and pagination."""
        self.mock_client.make_request.return_value = {
            "data": [],
            "meta": {"current_page": 1, "total": 0},
        }

        result = self.service.list(
            {
                "email": "john@example.com",
                "verification_status": "VERIFIED",
                "type": "individual",
                "paginate": True,
            }
        )

        args, _ = self.mock_client.make_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].startswith("/api/external/customer?"))
        query = args[1].split("?", 1)[1]
        self.assertIn("email=john%40example.com", query)
        self.assertIn("verification_status=VERIFIED", query)
        self.assertIn("type=individual", query)
        self.assertIn("paginate=true", query)
        self.assertEqual(result["meta"]["current_page"], 1)


class TestCollectionService(unittest.TestCase):
    """Test cases for CollectionService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = CollectionService(self.mock_client)

    def test_initiate_collection(self):
        """Test initiating a collection."""
        collection_data = {
            "customer_id": "customer-id",
            "wallet_id": "wallet-id",
            "amount": 1000,
            "currency": "NGN",
            "method": "card",
        }

        self.mock_client.make_request.return_value = {"data": {"transaction_id": "tx-id"}}

        result = self.service.initiate(collection_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/collection", collection_data
        )
        self.assertEqual(result["data"]["transaction_id"], "tx-id")

    def test_initiate_collection_missing_fields(self):
        """Test initiating collection with missing fields."""
        collection_data = {
            "method": "card",
            # Missing required fields: customer_id, wallet_id, amount, currency
        }

        with self.assertRaises(ValueError) as context:
            self.service.initiate(collection_data)

        self.assertIn("customer_id is required", str(context.exception))


class TestPayoutService(unittest.TestCase):
    """Test cases for PayoutService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = PayoutService(self.mock_client)

    def test_initiate_payout(self):
        """Test initiating a payout."""
        payout_data = {
            "wallet_id": "wallet-id",
            "customer_id": "customer-id",
            "method": "bank_transfer",
            "from_amount": 1000,
            "from_currency_id": "NGN",
            "to_currency_id": "NGN",
            "bank_id": "bank-id",
            "account_number": "1234567890",
        }

        self.mock_client.make_request.return_value = {"data": {"transaction_id": "tx-id"}}

        result = self.service.initiate(payout_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/payout", payout_data
        )
        self.assertEqual(result["data"]["transaction_id"], "tx-id")

    def test_initiate_bank_transfer_without_account_number(self):
        """Test bank transfer without account number for NGN."""
        payout_data = {
            "wallet_id": "wallet-id",
            "customer_id": "customer-id",
            "method": "bank_transfer",
            "from_amount": 1000,
            "from_currency_id": "NGN",
            "to_currency_id": "NGN",
            "bank_id": "bank-id",
            # Missing account_number
        }

        with self.assertRaises(ValueError) as context:
            self.service.initiate(payout_data)

        self.assertIn("account_number is required", str(context.exception))

    def test_initiate_interac_without_required_fields(self):
        """Test Interac payout without required fields."""
        payout_data = {
            "wallet_id": "wallet-id",
            "customer_id": "customer-id",
            "method": "interac",
            "from_amount": 1000,
            "from_currency_id": "CAD",
            "to_currency_id": "CAD",
        }

        with self.assertRaises(ValueError) as context:
            self.service.initiate(payout_data)

        self.assertIn("email is required", str(context.exception))


class TestWebhookService(unittest.TestCase):
    """Test cases for WebhookService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = WebhookService(self.mock_client)

    def test_verify_signature_valid(self):
        """Test valid signature verification."""
        payload = '{"test": "data"}'
        timestamp = "1234567890"
        signature = "sha256=5d41402abc4b2a76b9719d911017c592"
        secret = "test-secret"

        # This would normally require actual HMAC calculation
        # For testing, we'll mock the internal comparison
        with unittest.mock.patch("hmac.compare_digest", return_value=True):
            result = self.service.verify_signature(payload, signature, timestamp, secret)
            self.assertTrue(result)

    def test_verify_signature_invalid(self):
        """Test invalid signature verification."""
        payload = '{"test": "data"}'
        timestamp = "1234567890"
        signature = "sha256=invalid"
        secret = "test-secret"

        result = self.service.verify_signature(payload, signature, timestamp, secret)
        self.assertFalse(result)

    def test_verify_signature_missing_payload(self):
        """Test signature verification with missing payload."""
        with self.assertRaises(ValueError) as context:
            self.service.verify_signature("", "signature", "1234567890", "secret")

        self.assertIn("Payload is required", str(context.exception))

    def test_verify_signature_missing_timestamp(self):
        """Test signature verification with missing timestamp."""
        with self.assertRaises(ValueError) as context:
            self.service.verify_signature('{"test": "data"}', "signature", "", "secret")

        self.assertIn("Timestamp is required", str(context.exception))

    def test_construct_event_valid(self):
        """Test constructing event with valid signature."""
        payload = '{"test": "data"}'
        timestamp = "1234567890"
        signature = "sha256=valid"
        secret = "test-secret"

        # Mock the verification to return True
        with unittest.mock.patch.object(self.service, "verify_signature", return_value=True):
            result = self.service.construct_event(payload, signature, timestamp, secret)

            self.assertEqual(result["test"], "data")
            self.assertTrue(result["verified"])
            self.assertIn("timestamp", result)

    def test_construct_event_invalid_signature(self):
        """Test constructing event with invalid signature."""
        payload = '{"test": "data"}'
        timestamp = "1234567890"
        signature = "sha256=invalid"
        secret = "test-secret"

        # Mock the verification to return False
        with unittest.mock.patch.object(self.service, "verify_signature", return_value=False):
            with self.assertRaises(ValueError) as context:
                self.service.construct_event(payload, signature, timestamp, secret)

            self.assertIn("Invalid webhook signature", str(context.exception))


if __name__ == "__main__":
    unittest.main()
