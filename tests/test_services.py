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
    RateService,
    SwapService,
    RefundService,
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

    def test_create_business_customer_success(self):
        """Business customers identify via registration_number + incorporation_country."""
        customer_data = {
            "type": "business",
            "email": "acme@example.com",
            "country": "NG",
            "business_name": "Acme Inc",
            "registration_number": "RC123456",
            "incorporation_country": "NG",
        }

        self.mock_client.make_request.return_value = {"data": {"id": "customer-id"}}

        result = self.service.create(customer_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer", customer_data
        )
        self.assertEqual(result["data"]["id"], "customer-id")

    def test_create_business_customer_missing_business_name(self):
        """Test business customer creation without business name."""
        customer_data = {
            "type": "business",
            "email": "john@example.com",
            "country": "NG",
            "registration_number": "RC123456",
            "incorporation_country": "NG",
        }

        with self.assertRaises(ValueError) as context:
            self.service.create(customer_data)

        self.assertIn("business_name is required", str(context.exception))

    def test_create_business_customer_missing_registration_number(self):
        """Business customers require a registration_number."""
        customer_data = {
            "type": "business",
            "email": "john@example.com",
            "country": "NG",
            "business_name": "Acme Inc",
            "incorporation_country": "NG",
        }

        with self.assertRaises(ValueError) as context:
            self.service.create(customer_data)

        self.assertIn("registration_number is required", str(context.exception))

    def test_create_business_customer_does_not_require_id_type(self):
        """id_type/id_number are individual-only and not required for businesses."""
        customer_data = {
            "type": "business",
            "email": "acme@example.com",
            "country": "NG",
            "business_name": "Acme Inc",
            "registration_number": "RC123456",
            "incorporation_country": "NG",
        }

        self.mock_client.make_request.return_value = {"data": {"id": "customer-id"}}

        # No id_type / id_number provided; must not raise.
        self.service.create(customer_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer", customer_data
        )

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

    def test_upload_files_uses_post(self):
        """File association uses POST, not PUT."""
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.upload_files("customer-id", {"id_file": "file-id"})

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer/customer-id/files", {"id_file": "file-id"}
        )

    def test_submit(self):
        """Submit posts to the submit endpoint with no body."""
        self.mock_client.make_request.return_value = {"message": "ok"}

        self.service.submit("customer-id")

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer/customer-id/submit"
        )

    def test_submit_without_id(self):
        """Submit requires a customer ID."""
        with self.assertRaises(ValueError) as context:
            self.service.submit("")

        self.assertIn("Customer ID is required", str(context.exception))

    def test_upgrade_kyb_scope(self):
        """Upgrading KYB scope forwards the owners array."""
        upgrade_data = {"owners": [{"ownership_percentage": 100}]}
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.upgrade_kyb_scope("customer-id", upgrade_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer/customer-id/upgrade-kyb-scope", upgrade_data
        )

    def test_upgrade_kyb_scope_missing_owners(self):
        """Upgrading KYB scope requires a non-empty owners array."""
        with self.assertRaises(ValueError) as context:
            self.service.upgrade_kyb_scope("customer-id", {"owners": []})

        self.assertIn("owners is required", str(context.exception))

    def test_delete_owner(self):
        """Deleting an owner targets the owner endpoint."""
        self.mock_client.make_request.return_value = {"message": "ok"}

        self.service.delete_owner("customer-id", "owner-id")

        self.mock_client.make_request.assert_called_once_with(
            "DELETE", "/api/external/customer/customer-id/owner/owner-id"
        )

    def test_delete_owner_missing_owner_id(self):
        """Deleting an owner requires an owner ID."""
        with self.assertRaises(ValueError) as context:
            self.service.delete_owner("customer-id", "")

        self.assertIn("Owner ID is required", str(context.exception))

    def test_get_owner_file_presigned_url(self):
        """Owner file presigned URL requires file_category."""
        data = {"file_category": "id_document_front"}
        self.mock_client.make_request.return_value = {"file_id": "f", "url": "u"}

        self.service.get_owner_file_presigned_url("customer-id", "owner-id", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST",
            "/api/external/customer/customer-id/owner/owner-id/file/presigned-url",
            data,
        )

    def test_get_owner_file_presigned_url_missing_category(self):
        """Owner file presigned URL fails without file_category."""
        with self.assertRaises(ValueError) as context:
            self.service.get_owner_file_presigned_url("customer-id", "owner-id", {})

        self.assertIn("file_category is required", str(context.exception))

    def test_upload_owner_files(self):
        """Owner file association requires id_document_front."""
        data = {"id_document_front": "file-uuid"}
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.upload_owner_files("customer-id", "owner-id", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer/customer-id/owner/owner-id/files", data
        )

    def test_upload_owner_files_missing_front(self):
        """Owner file association fails without id_document_front."""
        with self.assertRaises(ValueError) as context:
            self.service.upload_owner_files("customer-id", "owner-id", {})

        self.assertIn("id_document_front is required", str(context.exception))

    def test_list_documents(self):
        """Listing documents targets the document endpoint."""
        self.mock_client.make_request.return_value = {"data": []}

        self.service.list_documents("customer-id")

        self.mock_client.make_request.assert_called_once_with(
            "GET", "/api/external/customer/customer-id/document"
        )

    def test_get_document(self):
        """Getting a document targets the document by ID."""
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.get_document("customer-id", "doc-id")

        self.mock_client.make_request.assert_called_once_with(
            "GET", "/api/external/customer/customer-id/document/doc-id"
        )

    def test_get_document_presigned_url(self):
        """Document presigned URL posts with no body."""
        self.mock_client.make_request.return_value = {"file_id": "f", "url": "u"}

        self.service.get_document_presigned_url("customer-id")

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer/customer-id/document/presigned-url"
        )

    def test_create_document(self):
        """Creating a document requires type, name and file_id."""
        data = {"type": "PROOF_OF_ADDRESS", "name": "Utility bill", "file_id": "file-uuid"}
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.create_document("customer-id", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/customer/customer-id/document", data
        )

    def test_create_document_missing_file_id(self):
        """Creating a document fails without file_id."""
        with self.assertRaises(ValueError) as context:
            self.service.create_document(
                "customer-id", {"type": "PROOF_OF_ADDRESS", "name": "Utility bill"}
            )

        self.assertIn("file_id is required", str(context.exception))

    def test_update_document(self):
        """Updating a document targets the document by ID via PUT."""
        data = {"name": "Renamed"}
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.update_document("customer-id", "doc-id", data)

        self.mock_client.make_request.assert_called_once_with(
            "PUT", "/api/external/customer/customer-id/document/doc-id", data
        )

    def test_delete_document(self):
        """Deleting a document targets the document by ID via DELETE."""
        self.mock_client.make_request.return_value = {"message": "ok"}

        self.service.delete_document("customer-id", "doc-id")

        self.mock_client.make_request.assert_called_once_with(
            "DELETE", "/api/external/customer/customer-id/document/doc-id"
        )

    def test_upload_file_complete_identity_back_mapping(self):
        """identity_back maps to the id_file_back association field."""
        self.mock_client.make_request.side_effect = [
            {"data": {"file_id": "file-id", "url": "https://s3/presigned"}},
            {"data": {"message": "associated"}},
        ]

        with unittest.mock.patch.object(self.service, "_upload_to_s3", return_value=None):
            result = self.service.upload_file_complete(
                "customer-id",
                {
                    "file": b"\xff\xd8\xff\xe0binary",
                    "file_category": "identity_back",
                    "content_type": "image/jpeg",
                },
            )

        # Second call associates the uploaded file under the id_file_back field.
        association_call = self.mock_client.make_request.call_args_list[1]
        self.assertEqual(
            association_call.args[0:2],
            ("POST", "/api/external/customer/customer-id/files"),
        )
        self.assertEqual(association_call.args[2], {"id_file_back": "file-id"})
        self.assertEqual(result["file_id"], "file-id")

    def test_upload_file_complete_rejects_unknown_category(self):
        """Unknown file categories are rejected up front."""
        with self.assertRaises(ValueError) as context:
            self.service.upload_file_complete(
                "customer-id", {"file": b"x", "file_category": "passport"}
            )

        self.assertIn("file_category must be one of", str(context.exception))


class TestCollectionService(unittest.TestCase):
    """Test cases for CollectionService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = CollectionService(self.mock_client)

    def test_initiate_collection(self):
        """Test initiating a card collection."""
        collection_data = {
            "method": "card",
            "amount": 1000,
            "wallet_id": "wallet-id",
            "customer_id": "customer-id",
            "card_holder_name": "John Doe",
            "card_number": "4111111111111111",
            "expiry": "12/28",
            "cvc": "123",
        }

        self.mock_client.make_request.return_value = {"data": {"transaction_id": "tx-id"}}

        result = self.service.initiate(collection_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/collection", collection_data
        )
        self.assertEqual(result["data"]["transaction_id"], "tx-id")

    def test_initiate_open_banking_collection(self):
        """Open banking collections need only method, amount and wallet_id."""
        collection_data = {
            "method": "open_banking",
            "amount": 1000,
            "wallet_id": "wallet-id",
            "merchant_reference": "order-123",
        }

        self.mock_client.make_request.return_value = {"transaction_id": "tx-id", "url": "https://x"}

        result = self.service.initiate(collection_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/collection", collection_data
        )
        self.assertEqual(result["transaction_id"], "tx-id")

    def test_initiate_collection_missing_fields(self):
        """Test initiating collection with missing base fields."""
        collection_data = {
            "method": "card",
            # Missing required base fields: amount, wallet_id
        }

        with self.assertRaises(ValueError) as context:
            self.service.initiate(collection_data)

        self.assertIn("amount is required", str(context.exception))

    def test_initiate_card_collection_missing_card_fields(self):
        """Card collections require the card details up front."""
        collection_data = {
            "method": "card",
            "amount": 1000,
            "wallet_id": "wallet-id",
            # Missing customer_id and card fields
        }

        with self.assertRaises(ValueError) as context:
            self.service.initiate(collection_data)

        self.assertIn("customer_id is required for card method", str(context.exception))

    def test_initiate_crypto_missing_fields(self):
        """Crypto collections require amount, wallet_id, network and token."""
        with self.assertRaises(ValueError) as context:
            self.service.initiate_crypto({"amount": 100, "wallet_id": "wallet-id"})

        self.assertIn("network is required", str(context.exception))

    def test_get_crypto_networks_with_filters(self):
        """Crypto networks accept an optional transaction_type filter."""
        self.mock_client.make_request.return_value = {"data": []}

        self.service.get_crypto_networks({"transaction_type": "payout"})

        args, _ = self.mock_client.make_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].startswith("/api/external/collection/crypto/networks?"))
        self.assertIn("transaction_type=payout", args[1])

    def test_initiate_interac_money_request(self):
        """Interac money requests require amount and email."""
        request_data = {"amount": 100, "email": "payer@example.com"}
        self.mock_client.make_request.return_value = {"transaction_id": "tx-id"}

        self.service.initiate_interac_money_request(request_data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/collection/interac-money-request", request_data
        )

    def test_initiate_interac_money_request_missing_email(self):
        """Interac money requests fail without an email."""
        with self.assertRaises(ValueError) as context:
            self.service.initiate_interac_money_request({"amount": 100})

        self.assertIn("email is required", str(context.exception))

    def test_accept_interac_money_request_missing_reference(self):
        """Accepting an Interac request requires a reference_number."""
        with self.assertRaises(ValueError) as context:
            self.service.accept_interac_money_request({})

        self.assertIn("reference_number is required", str(context.exception))


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

    def test_initiate_payout_forwards_merchant_reference(self):
        """An optional merchant_reference is forwarded verbatim to the API."""
        payout_data = {
            "wallet_id": "wallet-id",
            "customer_id": "customer-id",
            "method": "bank_transfer",
            "from_amount": 1000,
            "from_currency_id": "NGN",
            "to_currency_id": "NGN",
            "bank_id": "bank-id",
            "account_number": "1234567890",
            "merchant_reference": "order-9001",
        }

        self.mock_client.make_request.return_value = {"data": {"merchant_reference": "order-9001"}}

        self.service.initiate(payout_data)

        args, _ = self.mock_client.make_request.call_args
        self.assertEqual(args[2]["merchant_reference"], "order-9001")

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


class TestBankService(unittest.TestCase):
    """Test cases for BankService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = BankService(self.mock_client)

    def test_list_without_filters(self):
        """Listing banks without filters hits the bare endpoint."""
        self.mock_client.make_request.return_value = {"data": []}

        self.service.list()

        self.mock_client.make_request.assert_called_once_with("GET", "/api/external/bank")

    def test_list_with_filters(self):
        """Listing banks forwards currency/country filters as query params."""
        self.mock_client.make_request.return_value = {"data": []}

        self.service.list({"currency": "NGN", "country": "NG"})

        args, _ = self.mock_client.make_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].startswith("/api/external/bank?"))
        self.assertIn("currency=NGN", args[1])
        self.assertIn("country=NG", args[1])

    def test_verify_payee(self):
        """Payee verification requires sort_code, account_number and account_name."""
        data = {
            "sort_code": "123456",
            "account_number": "12345678",
            "account_name": "John Doe",
        }
        self.mock_client.make_request.return_value = {"matched": True}

        self.service.verify_payee(data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/bank/payee-verification", data
        )

    def test_verify_payee_missing_field(self):
        """Payee verification fails without account_name."""
        with self.assertRaises(ValueError) as context:
            self.service.verify_payee({"sort_code": "123456", "account_number": "12345678"})

        self.assertIn("account_name is required", str(context.exception))

    def test_verify_iban(self):
        """IBAN verification requires an iban."""
        data = {"iban": "DE89370400440532013000"}
        self.mock_client.make_request.return_value = {"sepa_reachable": True}

        self.service.verify_iban(data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", "/api/external/bank/iban-verification", data
        )

    def test_verify_iban_missing_iban(self):
        """IBAN verification fails without an iban."""
        with self.assertRaises(ValueError) as context:
            self.service.verify_iban({})

        self.assertIn("iban is required", str(context.exception))


class TestRateService(unittest.TestCase):
    """Test cases for RateService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = RateService(self.mock_client)

    def test_list_without_filters(self):
        """Listing rates without filters hits the bare endpoint."""
        self.mock_client.make_request.return_value = {"data": []}

        self.service.list()

        self.mock_client.make_request.assert_called_once_with("GET", "/api/external/rate")

    def test_list_with_search_term(self):
        """Listing rates forwards search_term as a query param."""
        self.mock_client.make_request.return_value = {"data": []}

        self.service.list({"search_term": "NGN"})

        args, _ = self.mock_client.make_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].startswith("/api/external/rate?"))
        self.assertIn("search_term=NGN", args[1])


class TestSwapService(unittest.TestCase):
    """Test cases for SwapService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = SwapService(self.mock_client)

    def test_initiate(self):
        """Initiating a swap requires the two wallet ids and an amount."""
        data = {
            "from_business_wallet_id": "wallet-a",
            "to_business_wallet_id": "wallet-b",
            "amount": 100,
        }
        self.mock_client.make_request.return_value = {"business_swap_transaction": {}}

        self.service.initiate(data)

        self.mock_client.make_request.assert_called_once_with("POST", "/api/external/swap", data)

    def test_initiate_missing_field(self):
        """Initiating a swap fails without the destination wallet."""
        with self.assertRaises(ValueError) as context:
            self.service.initiate({"from_business_wallet_id": "wallet-a", "amount": 100})

        self.assertIn("to_business_wallet_id is required", str(context.exception))


class TestRefundService(unittest.TestCase):
    """Test cases for RefundService."""

    def setUp(self):
        """Set up test service."""
        self.mock_client = MagicMock()
        self.service = RefundService(self.mock_client)

    def test_initiate(self):
        """Initiating a refund requires a transaction_id."""
        data = {"transaction_id": "tx-id", "reason": "duplicate"}
        self.mock_client.make_request.return_value = {"data": {"id": "refund-id"}}

        self.service.initiate(data)

        self.mock_client.make_request.assert_called_once_with("POST", "/api/external/refund", data)

    def test_initiate_missing_transaction_id(self):
        """Initiating a refund fails without a transaction_id."""
        with self.assertRaises(ValueError) as context:
            self.service.initiate({"reason": "duplicate"})

        self.assertIn("transaction_id is required", str(context.exception))

    def test_get(self):
        """Getting a refund targets the refund by ID."""
        self.mock_client.make_request.return_value = {"data": {"id": "refund-id"}}

        self.service.get("refund-id")

        self.mock_client.make_request.assert_called_once_with(
            "GET", "/api/external/refund/refund-id"
        )

    def test_get_missing_id(self):
        """Getting a refund fails without an ID."""
        with self.assertRaises(ValueError) as context:
            self.service.get("")

        self.assertIn("Refund ID is required", str(context.exception))


if __name__ == "__main__":
    unittest.main()
