"""
Tests for SignaService
"""

import unittest
from unittest.mock import MagicMock
from blaaiz.services.signa import SignaService

BASE_PATH = "/api/external/compliance/kyc/sessions"


class TestSignaServiceSessions(unittest.TestCase):
    """Session create/list/get/submit/cancel."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.service = SignaService(self.mock_client)

    def test_create_session(self):
        """Create posts the session data as-is to the sessions endpoint."""
        data = {
            "customer_reference": "customer-123",
            "idempotency_key": "request-123",
            "requirements": ["DOCUMENTS", "SELFIE"],
            "fulfilment_mode": "HOSTED",
            "applicant": {"first_name": "Ada", "country": "GBR"},
        }
        self.mock_client.make_request.return_value = {"data": {"id": "session-id"}}

        self.service.create_session(data)

        self.mock_client.make_request.assert_called_once_with("POST", BASE_PATH, data)

    def test_create_session_via_create_alias(self):
        """create delegates to create_session."""
        data = {
            "customer_reference": "customer-123",
            "idempotency_key": "request-123",
            "requirements": ["DOCUMENTS"],
        }
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.create(data)

        self.mock_client.make_request.assert_called_once_with("POST", BASE_PATH, data)

    def test_list_sessions_with_limit_and_offset(self):
        """Limit/offset filters are sent as a query string."""
        self.mock_client.make_request.return_value = {"data": {"sessions": []}}

        self.service.list_sessions({"limit": 25, "offset": 50})

        self.mock_client.make_request.assert_called_once_with(
            "GET", f"{BASE_PATH}?limit=25&offset=50"
        )

    def test_list_sessions_no_filters_has_no_question_mark(self):
        """No filters means the bare endpoint, without a trailing '?'."""
        self.mock_client.make_request.return_value = {"data": {"sessions": []}}

        self.service.list_sessions()

        self.mock_client.make_request.assert_called_once_with("GET", BASE_PATH)

    def test_list_sessions_via_list_alias(self):
        """list delegates to list_sessions."""
        self.mock_client.make_request.return_value = {"data": {"sessions": []}}

        self.service.list({"limit": 10})

        self.mock_client.make_request.assert_called_once_with("GET", f"{BASE_PATH}?limit=10")

    def test_get_submit_and_cancel_encode_the_session_id(self):
        """A session id containing '/' is percent-encoded as a single path segment."""
        self.mock_client.make_request.return_value = {"data": {"id": "session/123"}}

        self.service.get_session("session/123")
        self.service.submit_session("session/123")
        self.service.cancel_session("session/123")

        self.assertEqual(
            [call.args for call in self.mock_client.make_request.call_args_list],
            [
                ("GET", f"{BASE_PATH}/session%2F123"),
                ("POST", f"{BASE_PATH}/session%2F123/submit"),
                ("POST", f"{BASE_PATH}/session%2F123/cancel"),
            ],
        )

    def test_get_via_get_alias(self):
        """get delegates to get_session."""
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.get("session-123")

        self.mock_client.make_request.assert_called_once_with("GET", f"{BASE_PATH}/session-123")

    def test_submit_via_submit_alias(self):
        """submit delegates to submit_session."""
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.submit("session-123")

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/submit"
        )

    def test_cancel_via_cancel_alias(self):
        """cancel delegates to cancel_session."""
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.cancel("session-123")

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/cancel"
        )


class TestSignaServiceDocuments(unittest.TestCase):
    """Upload URL, document upload, and verification link."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.service = SignaService(self.mock_client)

    def test_create_document_upload_url(self):
        """Upload-url data is forwarded unchanged to the upload-url endpoint."""
        data = {"file_name": "passport.jpg", "id_doc_type": "PASSPORT"}
        self.mock_client.make_request.return_value = {"data": {"url": "https://upload"}}

        self.service.create_document_upload_url("session-123", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/documents/upload-url", data
        )

    def test_upload_session_document_inline(self):
        """Inline uploads send content_base64 straight through."""
        data = {
            "filename": "passport.jpg",
            "content_type": "image/jpeg",
            "id_doc_type": "PASSPORT",
            "country": "GBR",
            "content_base64": "aGVsbG8=",
        }
        self.mock_client.make_request.return_value = {"data": {"id": "session-123"}}

        self.service.upload_session_document("session-123", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/documents", data
        )

    def test_upload_staged_document_via_upload_document_alias(self):
        """upload_document delegates to upload_session_document."""
        data = {
            "filename": "passport.jpg",
            "content_type": "image/jpeg",
            "id_doc_type": "PASSPORT",
            "country": "GBR",
            "file_name": "a1b2c3_passport.jpg",
        }
        self.mock_client.make_request.return_value = {"data": {"id": "session-123"}}

        self.service.upload_document("session-123", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/documents", data
        )

    def test_issue_verification_link_sends_no_body(self):
        """The verification-link endpoint is a bare POST with no body."""
        self.mock_client.make_request.return_value = {"data": {"verification_link": "https://x"}}

        self.service.issue_verification_link("session-123")

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/verification-link"
        )


class TestSignaServiceValidation(unittest.TestCase):
    """Client-side validation that runs before any request."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.service = SignaService(self.mock_client)

    def _assert_no_http_call(self):
        self.mock_client.make_request.assert_not_called()

    # -- Session id presence, for every method that takes one --

    def test_get_session_requires_id(self):
        with self.assertRaises(ValueError) as context:
            self.service.get_session("")
        self.assertEqual(str(context.exception), "Session ID is required")
        self._assert_no_http_call()

    def test_submit_session_requires_id(self):
        with self.assertRaises(ValueError) as context:
            self.service.submit_session("")
        self.assertEqual(str(context.exception), "Session ID is required")
        self._assert_no_http_call()

    def test_cancel_session_requires_id(self):
        with self.assertRaises(ValueError) as context:
            self.service.cancel_session("")
        self.assertEqual(str(context.exception), "Session ID is required")
        self._assert_no_http_call()

    def test_create_document_upload_url_requires_id(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_document_upload_url(
                "", {"file_name": "x.jpg", "id_doc_type": "PASSPORT"}
            )
        self.assertEqual(str(context.exception), "Session ID is required")
        self._assert_no_http_call()

    def test_upload_session_document_requires_id(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "",
                {
                    "filename": "x.jpg",
                    "content_type": "image/jpeg",
                    "id_doc_type": "PASSPORT",
                    "country": "GBR",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(str(context.exception), "Session ID is required")
        self._assert_no_http_call()

    def test_issue_verification_link_requires_id(self):
        with self.assertRaises(ValueError) as context:
            self.service.issue_verification_link("")
        self.assertEqual(str(context.exception), "Session ID is required")
        self._assert_no_http_call()

    # -- createSession --

    def test_create_session_requires_data(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session(None)
        self.assertEqual(str(context.exception), "Session data is required")
        self._assert_no_http_call()

    def test_create_session_rejects_non_map_data(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session(["DOCUMENTS"])
        self.assertEqual(str(context.exception), "Session data is required")
        self._assert_no_http_call()

    def test_create_session_requires_customer_reference(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session({"idempotency_key": "k", "requirements": ["DOCUMENTS"]})
        self.assertEqual(str(context.exception), "customer_reference is required")
        self._assert_no_http_call()

    def test_create_session_requires_idempotency_key(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session({"customer_reference": "c", "requirements": ["DOCUMENTS"]})
        self.assertEqual(str(context.exception), "idempotency_key is required")
        self._assert_no_http_call()

    def test_create_session_requires_requirements(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session({"customer_reference": "c", "idempotency_key": "k"})
        self.assertEqual(str(context.exception), "requirements is required")
        self._assert_no_http_call()

    def test_create_session_requirements_must_be_non_empty_array(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session(
                {"customer_reference": "c", "idempotency_key": "k", "requirements": []}
            )
        self.assertEqual(str(context.exception), "requirements must be a non-empty array")
        self._assert_no_http_call()

    def test_create_session_requirements_must_be_a_list(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session(
                {
                    "customer_reference": "c",
                    "idempotency_key": "k",
                    "requirements": "DOCUMENTS",
                }
            )
        self.assertEqual(str(context.exception), "requirements must be a non-empty array")
        self._assert_no_http_call()

    def test_create_session_rejects_unknown_requirement(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session(
                {
                    "customer_reference": "customer-123",
                    "idempotency_key": "request-123",
                    "requirements": ["UNKNOWN"],
                }
            )
        self.assertEqual(
            str(context.exception),
            "requirements must contain only: DOCUMENTS, SELFIE, FACE_MATCH, PROOF_OF_ADDRESS",
        )
        self._assert_no_http_call()

    def test_create_session_rejects_non_string_requirement(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_session(
                {
                    "customer_reference": "c",
                    "idempotency_key": "k",
                    "requirements": [123],
                }
            )
        self.assertEqual(
            str(context.exception),
            "requirements must contain only: DOCUMENTS, SELFIE, FACE_MATCH, PROOF_OF_ADDRESS",
        )
        self._assert_no_http_call()

    def test_create_session_requirements_are_case_insensitive(self):
        """Lowercase requirements pass validation; the server normalises them."""
        data = {
            "customer_reference": "c",
            "idempotency_key": "k",
            "requirements": ["documents", "selfie"],
        }
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.create_session(data)

        # Sent unchanged (still lowercase) - the SDK does not mutate caller data.
        self.mock_client.make_request.assert_called_once_with("POST", BASE_PATH, data)

    def test_create_session_does_not_validate_fulfilment_mode_or_applicant(self):
        """fulfilment_mode and applicant are left for the API to validate."""
        data = {
            "customer_reference": "c",
            "idempotency_key": "k",
            "requirements": ["DOCUMENTS"],
            "fulfilment_mode": "NOT_A_REAL_MODE",
            "applicant": "not-an-object",
        }
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.create_session(data)

        self.mock_client.make_request.assert_called_once_with("POST", BASE_PATH, data)

    # -- createDocumentUploadUrl --

    def test_create_document_upload_url_requires_data(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_document_upload_url("session-123", None)
        self.assertEqual(str(context.exception), "Document data is required")
        self._assert_no_http_call()

    def test_create_document_upload_url_requires_file_name(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_document_upload_url("session-123", {"id_doc_type": "PASSPORT"})
        self.assertEqual(str(context.exception), "file_name is required")
        self._assert_no_http_call()

    def test_create_document_upload_url_requires_id_doc_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_document_upload_url("session-123", {"file_name": "passport.jpg"})
        self.assertEqual(str(context.exception), "id_doc_type is required")
        self._assert_no_http_call()

    def test_create_document_upload_url_rejects_unknown_id_doc_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_document_upload_url(
                "session-123", {"file_name": "passport.jpg", "id_doc_type": "UNKNOWN"}
            )
        self.assertEqual(
            str(context.exception),
            "id_doc_type must be one of: PASSPORT, ID_CARD, DRIVERS, RESIDENCE_PERMIT, UTILITY_BILL, BANK_STATEMENT, SELFIE",
        )
        self._assert_no_http_call()

    def test_create_document_upload_url_rejects_non_string_id_doc_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.create_document_upload_url(
                "session-123", {"file_name": "passport.jpg", "id_doc_type": 7}
            )
        self.assertEqual(
            str(context.exception),
            "id_doc_type must be one of: PASSPORT, ID_CARD, DRIVERS, RESIDENCE_PERMIT, UTILITY_BILL, BANK_STATEMENT, SELFIE",
        )
        self._assert_no_http_call()

    # -- uploadSessionDocument --

    def test_upload_session_document_requires_data(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document("session-123", None)
        self.assertEqual(str(context.exception), "Document data is required")
        self._assert_no_http_call()

    def test_upload_session_document_requires_filename(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "content_type": "image/jpeg",
                    "id_doc_type": "PASSPORT",
                    "country": "GBR",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(str(context.exception), "filename is required")
        self._assert_no_http_call()

    def test_upload_session_document_requires_content_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "id_doc_type": "PASSPORT",
                    "country": "GBR",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(str(context.exception), "content_type is required")
        self._assert_no_http_call()

    def test_upload_session_document_requires_id_doc_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "content_type": "image/jpeg",
                    "country": "GBR",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(str(context.exception), "id_doc_type is required")
        self._assert_no_http_call()

    def test_upload_session_document_requires_country(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "content_type": "image/jpeg",
                    "id_doc_type": "PASSPORT",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(str(context.exception), "country is required")
        self._assert_no_http_call()

    def test_upload_session_document_rejects_unknown_content_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "content_type": "text/plain",
                    "id_doc_type": "PASSPORT",
                    "country": "GBR",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(
            str(context.exception),
            "content_type must be one of: image/jpeg, image/png, image/webp, application/pdf",
        )
        self._assert_no_http_call()

    def test_upload_session_document_rejects_unknown_id_doc_type(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "content_type": "image/jpeg",
                    "id_doc_type": "UNKNOWN",
                    "country": "GBR",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(
            str(context.exception),
            "id_doc_type must be one of: PASSPORT, ID_CARD, DRIVERS, RESIDENCE_PERMIT, UTILITY_BILL, BANK_STATEMENT, SELFIE",
        )
        self._assert_no_http_call()

    def test_upload_session_document_requires_exactly_one_transport_when_neither_given(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "content_type": "image/jpeg",
                    "id_doc_type": "PASSPORT",
                    "country": "GBR",
                },
            )
        self.assertEqual(
            str(context.exception), "Provide exactly one of file_name or content_base64"
        )
        self._assert_no_http_call()

    def test_upload_session_document_requires_exactly_one_transport_when_both_given(self):
        with self.assertRaises(ValueError) as context:
            self.service.upload_session_document(
                "session-123",
                {
                    "filename": "passport.jpg",
                    "content_type": "image/jpeg",
                    "id_doc_type": "PASSPORT",
                    "country": "GBR",
                    "file_name": "staged.jpg",
                    "content_base64": "aGVsbG8=",
                },
            )
        self.assertEqual(
            str(context.exception), "Provide exactly one of file_name or content_base64"
        )
        self._assert_no_http_call()

    def test_content_type_and_id_doc_type_are_case_insensitive(self):
        """Validation accepts mixed case; the SDK still sends the data unchanged."""
        data = {
            "filename": "passport.jpg",
            "content_type": "Image/JPEG",
            "id_doc_type": "passport",
            "country": "GBR",
            "content_base64": "aGVsbG8=",
        }
        self.mock_client.make_request.return_value = {"data": {}}

        self.service.upload_session_document("session-123", data)

        self.mock_client.make_request.assert_called_once_with(
            "POST", f"{BASE_PATH}/session-123/documents", data
        )


if __name__ == "__main__":
    unittest.main()
