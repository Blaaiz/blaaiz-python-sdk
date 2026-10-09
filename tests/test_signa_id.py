"""
Tests for SignaIdService
"""

import unittest
from unittest.mock import MagicMock
from blaaiz.services.signa_id import SignaIdService

BASE_PATH = "/api/external/signa-id"

RELEASE_REQUEST = {
    "idempotency_key": "release-123",
    "purpose": "Open your trading account",
    "scopes": ["identity", "id_document", "document_images"],
    "origin": "https://yourapp.com",
    "reference": "user_10482",
}


class TestSignaIdService(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.make_request.return_value = {"data": {}}
        self.service = SignaIdService(self.mock_client)

    def test_create_release_request(self):
        self.service.create_release_request(RELEASE_REQUEST)

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/release-requests", RELEASE_REQUEST
        )

    def test_exchange_release_code(self):
        self.service.exchange_release_code("a" * 43)

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/releases/exchange", {"code": "a" * 43}
        )

    def test_get_release_and_document_encode_ids(self):
        self.service.get_release("release/1")
        self.service.get_release_document("release/1", "doc/1")

        self.assertEqual(
            self.mock_client.make_request.call_args_list,
            [
                unittest.mock.call("GET", f"{BASE_PATH}/releases/release%2F1"),
                unittest.mock.call("GET", f"{BASE_PATH}/releases/release%2F1/documents/doc%2F1"),
            ],
        )

    def test_get_wallet_status_encodes_the_address(self):
        self.service.get_wallet_status("0xabc/def")

        self.mock_client.make_request.assert_called_once_with(
            "GET", "/api/v1/signa-id/public/wallets/0xabc%2Fdef/status"
        )

    def test_get_wallet_status_with_and_without_chain_id(self):
        self.service.get_wallet_status("0xabc")
        self.service.get_wallet_status("0xabc", chain_id=8453)

        self.assertEqual(
            self.mock_client.make_request.call_args_list,
            [
                unittest.mock.call("GET", "/api/v1/signa-id/public/wallets/0xabc/status"),
                unittest.mock.call(
                    "GET", "/api/v1/signa-id/public/wallets/0xabc/status?chain_id=8453"
                ),
            ],
        )

    def test_create_release_request_validation_makes_no_http_call(self):
        cases = [
            (None, "Release request data is required"),
            ({**RELEASE_REQUEST, "origin": ""}, "origin is required"),
            ({**RELEASE_REQUEST, "scopes": []}, "scopes must be a non-empty array"),
            ({**RELEASE_REQUEST, "scopes": ["selfie"]}, "scopes must contain only"),
            ({**RELEASE_REQUEST, "scopes": ["Identity"]}, "scopes must contain only"),
        ]
        for data, message in cases:
            with self.subTest(message=message, data=data):
                with self.assertRaises(ValueError) as context:
                    self.service.create_release_request(data)
                self.assertIn(message, str(context.exception))

        self.mock_client.make_request.assert_not_called()

    def test_ids_code_and_address_validation_makes_no_http_call(self):
        calls = [
            (lambda: self.service.exchange_release_code(""), "Release code is required"),
            (lambda: self.service.get_release(""), "Release ID is required"),
            (lambda: self.service.get_release_document("", "doc"), "Release ID is required"),
            (
                lambda: self.service.get_release_document("release-1", ""),
                "Document ID is required",
            ),
            (lambda: self.service.get_wallet_status(""), "Wallet address is required"),
        ]
        for call, message in calls:
            with self.subTest(message=message):
                with self.assertRaises(ValueError) as context:
                    call()
                self.assertIn(message, str(context.exception))

        self.mock_client.make_request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
