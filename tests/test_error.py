"""
Tests for Blaaiz Error Classes
"""

import unittest
from blaaiz.error import BlaaizError


class TestBlaaizError(unittest.TestCase):
    """Test cases for BlaaizError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = BlaaizError("Test error")
        self.assertEqual(error.message, "Test error")
        self.assertIsNone(error.status)
        self.assertIsNone(error.code)

    def test_error_with_status(self):
        """Test error creation with status code."""
        error = BlaaizError("Test error", status=400)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.status, 400)
        self.assertIsNone(error.code)

    def test_error_with_status_and_code(self):
        """Test error creation with status and code."""
        error = BlaaizError("Test error", status=400, code="BAD_REQUEST")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.status, 400)
        self.assertEqual(error.code, "BAD_REQUEST")

    def test_error_str_representation(self):
        """Test string representation of error."""
        error = BlaaizError("Test error", status=400, code="BAD_REQUEST")
        expected = "BlaaizError(400, BAD_REQUEST): Test error"
        self.assertEqual(str(error), expected)

    def test_error_str_with_status_only(self):
        """Test string representation with status only."""
        error = BlaaizError("Test error", status=400)
        expected = "BlaaizError(400): Test error"
        self.assertEqual(str(error), expected)

    def test_error_str_without_status(self):
        """Test string representation without status."""
        error = BlaaizError("Test error")
        expected = "BlaaizError: Test error"
        self.assertEqual(str(error), expected)

    def test_error_repr(self):
        """Test repr representation of error."""
        error = BlaaizError("Test error", status=400, code="BAD_REQUEST")
        expected = "BlaaizError(message='Test error', status=400, code='BAD_REQUEST')"
        self.assertEqual(repr(error), expected)

    def test_error_inheritance(self):
        """Test that BlaaizError inherits from Exception."""
        error = BlaaizError("Test error")
        self.assertIsInstance(error, Exception)


if __name__ == "__main__":
    unittest.main()
