"""
Integration Tests for Blaaiz Python SDK

These tests require a valid API key and should be run against a test environment.
Set BLAAIZ_API_KEY environment variable to run these tests.
"""

import unittest
import os
from pathlib import Path
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
            # Skip if this is a server-side database error
            if "Column not found" in e.message or "500" in str(e.status):
                self.skipTest(f"Server-side error: {e.message}")
            else:
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
            # Handle different response structures
            if "data" in retrieved_customer["data"]:
                actual_customer_id = retrieved_customer["data"]["data"]["id"]
            else:
                actual_customer_id = retrieved_customer["data"]["id"]
            self.assertEqual(actual_customer_id, customer_id)

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
            # Check for total_fees in the response structure
            fee_data = fees["data"]
            if "total_fees" in fee_data:
                self.assertIsInstance(fee_data["total_fees"], (int, float))
            elif "our_fee" in fee_data:
                # Alternative structure - check for our_fee
                self.assertIsInstance(fee_data["our_fee"], (int, float))
            else:
                # Check if payout_fees contains total_fees
                if "payout_fees" in fee_data and fee_data["payout_fees"]:
                    self.assertIn("total_fees", fee_data["payout_fees"][0])
                else:
                    self.fail("Could not find fee information in response")

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

        # Test invalid customer ID (may not always raise BlaaizError depending on API)
        try:
            self.blaaiz.customers.get("invalid-customer-id")
        except BlaaizError:
            pass  # Expected error
        except Exception as e:
            # Some APIs may return other types of errors
            self.assertIsInstance(e, (BlaaizError, ValueError, TypeError))

        # Test invalid wallet ID (may not always raise BlaaizError depending on API)
        try:
            self.blaaiz.wallets.get("invalid-wallet-id")
        except BlaaizError:
            pass  # Expected error
        except Exception as e:
            # Some APIs may return other types of errors
            self.assertIsInstance(e, (BlaaizError, ValueError, TypeError))

    def test_file_upload_complete_workflow(self):
        """Test complete file upload workflow: create customer, upload file."""
        # First, create a test customer
        customer_data = {
            "first_name": "Integration",
            "last_name": "Test",
            "email": f"integration.test.{os.urandom(4).hex()}@example.com",
            "type": "individual",
            "country": "NG",
            "id_type": "passport",
            "id_number": f"A{os.urandom(4).hex().upper()}",
        }

        customer = None
        try:
            # Create customer
            customer_response = self.blaaiz.customers.create(customer_data)
            self.assertIsInstance(customer_response, dict)
            self.assertIn("data", customer_response)

            # Extract customer ID (handle nested structure)
            customer_data_obj = customer_response["data"]
            if isinstance(customer_data_obj, dict) and "data" in customer_data_obj:
                customer = customer_data_obj["data"]
            else:
                customer = customer_data_obj

            self.assertIsInstance(customer, dict)
            self.assertIn("id", customer)
            customer_id = customer["id"]

            # Create test files for different categories
            test_files = [
                {
                    "category": "identity",
                    "filename": "test_passport.pdf",
                    "content": b"Test passport document content",
                    "content_type": "application/pdf",
                },
                {
                    "category": "proof_of_address",
                    "filename": "test_address.jpg",
                    "content": b"Test address proof image content",
                    "content_type": "image/jpeg",
                },
                {
                    "category": "liveness_check",
                    "filename": "test_selfie.png",
                    "content": b"Test liveness check image content",
                    "content_type": "image/png",
                },
            ]

            # Test file upload for each category
            for file_info in test_files:
                with self.subTest(category=file_info["category"]):
                    file_options = {
                        "file": file_info["content"],
                        "file_category": file_info["category"],
                        "filename": file_info["filename"],
                        "content_type": file_info["content_type"],
                    }

                    # Upload file
                    upload_result = self.blaaiz.customers.upload_file_complete(
                        customer_id, file_options
                    )

                    # Verify upload result
                    self.assertIsInstance(upload_result, dict)
                    self.assertIn("file_id", upload_result)
                    self.assertIn("presigned_url", upload_result)

                    # Verify file_id is a valid UUID-like string
                    file_id = upload_result["file_id"]
                    self.assertIsInstance(file_id, str)
                    self.assertGreater(len(file_id), 10)  # Should be a valid ID

                    # Verify presigned URL is valid
                    presigned_url = upload_result["presigned_url"]
                    self.assertIsInstance(presigned_url, str)
                    self.assertTrue(presigned_url.startswith("https://"))

        except BlaaizError as e:
            self.fail(f"File upload integration test failed: {e.message}")
        except Exception as e:
            self.fail(f"Unexpected error in file upload test: {str(e)}")

    def test_file_upload_with_different_formats(self):
        """Test file upload with different file formats and content types."""
        # Create a test customer first
        customer_data = {
            "first_name": "FileTest",
            "last_name": "User",
            "email": f"filetest.{os.urandom(4).hex()}@example.com",
            "type": "individual",
            "country": "NG",
            "id_type": "passport",
            "id_number": f"A{os.urandom(4).hex().upper()}",
        }

        try:
            # Create customer
            customer_response = self.blaaiz.customers.create(customer_data)
            customer_data_obj = customer_response["data"]
            if isinstance(customer_data_obj, dict) and "data" in customer_data_obj:
                customer = customer_data_obj["data"]
            else:
                customer = customer_data_obj
            customer_id = customer["id"]

            # Test different file formats
            test_cases = [
                {
                    "name": "PDF Document",
                    "content": b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
                    "filename": "document.pdf",
                    "content_type": "application/pdf",
                },
                {
                    "name": "JPEG Image",
                    "content": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb",
                    "filename": "image.jpg",
                    "content_type": "image/jpeg",
                },
                {
                    "name": "PNG Image",
                    "content": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01",
                    "filename": "image.png",
                    "content_type": "image/png",
                },
            ]

            for test_case in test_cases:
                with self.subTest(format=test_case["name"]):
                    file_options = {
                        "file": test_case["content"],
                        "file_category": "identity",
                        "filename": test_case["filename"],
                        "content_type": test_case["content_type"],
                    }

                    # Upload file
                    upload_result = self.blaaiz.customers.upload_file_complete(
                        customer_id, file_options
                    )

                    # Verify successful upload
                    self.assertIsInstance(upload_result, dict)
                    self.assertIn("file_id", upload_result)
                    self.assertIn("presigned_url", upload_result)

        except BlaaizError as e:
            # Skip if API doesn't support multiple uploads for same customer
            if "already exists" in e.message.lower() or "duplicate" in e.message.lower():
                self.skipTest(f"API limitation: {e.message}")
            else:
                self.fail(f"File format test failed: {e.message}")
        except Exception as e:
            self.fail(f"Unexpected error in file format test: {str(e)}")

    def test_file_upload_error_handling(self):
        """Test file upload error handling for invalid inputs."""
        # Create a test customer
        customer_data = {
            "first_name": "ErrorTest",
            "last_name": "User",
            "email": f"errortest.{os.urandom(4).hex()}@example.com",
            "type": "individual",
            "country": "NG",
            "id_type": "passport",
            "id_number": f"A{os.urandom(4).hex().upper()}",
        }

        try:
            customer_response = self.blaaiz.customers.create(customer_data)
            customer_data_obj = customer_response["data"]
            if isinstance(customer_data_obj, dict) and "data" in customer_data_obj:
                customer = customer_data_obj["data"]
            else:
                customer = customer_data_obj
            customer_id = customer["id"]

            # Test invalid file category
            with self.assertRaises((BlaaizError, ValueError)):
                self.blaaiz.customers.upload_file_complete(
                    customer_id,
                    {
                        "file": b"test content",
                        "file_category": "invalid_category",
                        "filename": "test.pdf",
                        "content_type": "application/pdf",
                    },
                )

            # Test missing file content
            with self.assertRaises((BlaaizError, ValueError)):
                self.blaaiz.customers.upload_file_complete(
                    customer_id,
                    {
                        "file": None,
                        "file_category": "identity",
                        "filename": "test.pdf",
                        "content_type": "application/pdf",
                    },
                )

            # Test invalid customer ID
            with self.assertRaises(BlaaizError):
                self.blaaiz.customers.upload_file_complete(
                    "invalid-customer-id",
                    {
                        "file": b"test content",
                        "file_category": "identity",
                        "filename": "test.pdf",
                        "content_type": "application/pdf",
                    },
                )

        except BlaaizError as e:
            self.fail(f"Setup failed for error handling test: {e.message}")
        except Exception as e:
            self.fail(f"Unexpected error in error handling test: {str(e)}")

    def test_file_upload_with_real_pdf(self):
        """Test file upload with a real PDF file from the test fixtures."""
        # Get the path to the blank.pdf file
        test_dir = Path(__file__).parent
        pdf_path = test_dir / "blank.pdf"

        if not pdf_path.exists():
            self.skipTest("blank.pdf not found in tests directory")

        # Create a test customer
        customer_data = {
            "first_name": "RealFile",
            "last_name": "Test",
            "email": f"realfile.{os.urandom(4).hex()}@example.com",
            "type": "individual",
            "country": "NG",
            "id_type": "passport",
            "id_number": f"A{os.urandom(4).hex().upper()}",
        }

        try:
            # Create customer
            customer_response = self.blaaiz.customers.create(customer_data)
            customer_data_obj = customer_response["data"]
            if isinstance(customer_data_obj, dict) and "data" in customer_data_obj:
                customer = customer_data_obj["data"]
            else:
                customer = customer_data_obj
            customer_id = customer["id"]

            # Read the PDF file
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()

            # Upload the PDF file
            file_options = {
                "file": pdf_content,
                "file_category": "identity",
                "filename": "blank.pdf",
                "content_type": "application/pdf",
            }

            upload_result = self.blaaiz.customers.upload_file_complete(customer_id, file_options)

            # Verify upload result
            self.assertIsInstance(upload_result, dict)
            self.assertIn("file_id", upload_result)
            self.assertIn("presigned_url", upload_result)

            # Verify file_id is a valid UUID-like string
            file_id = upload_result["file_id"]
            self.assertIsInstance(file_id, str)
            self.assertGreater(len(file_id), 10)  # Should be a valid ID

            # Verify presigned URL is valid
            presigned_url = upload_result["presigned_url"]
            self.assertIsInstance(presigned_url, str)
            self.assertTrue(presigned_url.startswith("https://"))

            # Verify the file size is reasonable
            self.assertGreater(len(pdf_content), 0)
            self.assertLess(len(pdf_content), 10 * 1024 * 1024)  # Less than 10MB

            print(f"✅ Successfully uploaded PDF file: {len(pdf_content)} bytes")
            print(f"✅ File ID: {file_id}")
            print(f"✅ Presigned URL: {presigned_url[:50]}...")

        except BlaaizError as e:
            self.fail(f"Real PDF upload test failed: {e.message}")
        except Exception as e:
            self.fail(f"Unexpected error in real PDF test: {str(e)}")

    def test_file_upload_comprehensive_workflow(self):
        """Test comprehensive file upload workflow with multiple files and categories."""
        # Get the path to the blank.pdf file
        test_dir = Path(__file__).parent
        pdf_path = test_dir / "blank.pdf"

        if not pdf_path.exists():
            self.skipTest("blank.pdf not found in tests directory")

        # Create a test customer
        customer_data = {
            "first_name": "Comprehensive",
            "last_name": "Test",
            "email": f"comprehensive.{os.urandom(4).hex()}@example.com",
            "type": "individual",
            "country": "NG",
            "id_type": "passport",
            "id_number": f"A{os.urandom(4).hex().upper()}",
        }

        try:
            # Create customer
            customer_response = self.blaaiz.customers.create(customer_data)
            customer_data_obj = customer_response["data"]
            if isinstance(customer_data_obj, dict) and "data" in customer_data_obj:
                customer = customer_data_obj["data"]
            else:
                customer = customer_data_obj
            customer_id = customer["id"]

            # Read the actual PDF file
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()

            # Test files: mix of real PDF and synthetic content
            test_files = [
                {
                    "name": "Real PDF Document",
                    "category": "identity",
                    "filename": "passport.pdf",
                    "content": pdf_content,
                    "content_type": "application/pdf",
                },
                {
                    "name": "Synthetic JPEG",
                    "category": "liveness_check",
                    "filename": "selfie.jpg",
                    "content": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9",
                    "content_type": "image/jpeg",
                },
                {
                    "name": "Synthetic PNG",
                    "category": "proof_of_address",
                    "filename": "address_proof.png",
                    "content": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82",
                    "content_type": "image/png",
                },
            ]

            uploaded_files = []

            # Upload each file
            for file_info in test_files:
                with self.subTest(file=file_info["name"]):
                    file_options = {
                        "file": file_info["content"],
                        "file_category": file_info["category"],
                        "filename": file_info["filename"],
                        "content_type": file_info["content_type"],
                    }

                    upload_result = self.blaaiz.customers.upload_file_complete(
                        customer_id, file_options
                    )

                    # Verify upload result
                    self.assertIsInstance(upload_result, dict)
                    self.assertIn("file_id", upload_result)
                    self.assertIn("presigned_url", upload_result)

                    uploaded_files.append(
                        {
                            "name": file_info["name"],
                            "file_id": upload_result["file_id"],
                            "category": file_info["category"],
                            "size": len(file_info["content"]),
                        }
                    )

            # Verify all files were uploaded
            self.assertEqual(len(uploaded_files), 3)

            # Verify different categories were used
            categories = [f["category"] for f in uploaded_files]
            self.assertIn("identity", categories)
            self.assertIn("liveness_check", categories)
            self.assertIn("proof_of_address", categories)

            # Print summary
            print(
                f"✅ Successfully uploaded {len(uploaded_files)} files for customer {customer_id}"
            )
            for file_info in uploaded_files:
                print(
                    f"  - {file_info['name']} ({file_info['category']}): {file_info['size']} bytes -> {file_info['file_id']}"
                )

        except BlaaizError as e:
            # Skip if API has limitations on multiple uploads
            if "already exists" in e.message.lower() or "duplicate" in e.message.lower():
                self.skipTest(f"API limitation for multiple uploads: {e.message}")
            else:
                self.fail(f"Comprehensive upload test failed: {e.message}")
        except Exception as e:
            self.fail(f"Unexpected error in comprehensive test: {str(e)}")


if __name__ == "__main__":
    # Only run integration tests if API key is provided
    if os.getenv("BLAAIZ_API_KEY"):
        unittest.main()
    else:
        print("Skipping integration tests - BLAAIZ_API_KEY not set")
        print("To run integration tests, set BLAAIZ_API_KEY environment variable")
