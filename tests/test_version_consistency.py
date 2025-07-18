"""
Test version consistency across all files
"""

import re
import unittest
from pathlib import Path

import blaaiz


class TestVersionConsistency(unittest.TestCase):
    """Test that version numbers are consistent across all files."""

    def setUp(self):
        """Set up test case."""
        self.project_root = Path(__file__).parent.parent
        self.expected_version = blaaiz.__version__

    def test_pyproject_toml_version(self):
        """Test that pyproject.toml version matches __init__.py version."""
        pyproject_path = self.project_root / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Find version in pyproject.toml
        version_match = re.search(r'version = "([^"]+)"', content)
        self.assertIsNotNone(version_match, "Version not found in pyproject.toml")
        
        pyproject_version = version_match.group(1)
        self.assertEqual(
            pyproject_version,
            self.expected_version,
            f"pyproject.toml version ({pyproject_version}) doesn't match __init__.py version ({self.expected_version})"
        )

    def test_setup_py_version(self):
        """Test that setup.py version matches __init__.py version."""
        setup_path = self.project_root / "setup.py"
        if setup_path.exists():
            content = setup_path.read_text()
            
            # Find version in setup.py
            version_match = re.search(r'version="([^"]+)"', content)
            self.assertIsNotNone(version_match, "Version not found in setup.py")
            
            setup_version = version_match.group(1)
            self.assertEqual(
                setup_version,
                self.expected_version,
                f"setup.py version ({setup_version}) doesn't match __init__.py version ({self.expected_version})"
            )

    def test_user_agent_versions(self):
        """Test that User-Agent strings contain the correct version."""
        # Check client.py
        client_path = self.project_root / "blaaiz" / "client.py"
        content = client_path.read_text()
        
        user_agent_match = re.search(r'"User-Agent": "Blaaiz-Python-SDK/([^"]+)"', content)
        self.assertIsNotNone(user_agent_match, "User-Agent not found in client.py")
        
        client_version = user_agent_match.group(1)
        self.assertEqual(
            client_version,
            self.expected_version,
            f"client.py User-Agent version ({client_version}) doesn't match __init__.py version ({self.expected_version})"
        )

    def test_customer_service_user_agent(self):
        """Test that customer service User-Agent contains the correct version."""
        customer_path = self.project_root / "blaaiz" / "services" / "customer.py"
        content = customer_path.read_text()
        
        user_agent_match = re.search(r'"User-Agent": "Blaaiz-Python-SDK/([^"]+)"', content)
        self.assertIsNotNone(user_agent_match, "User-Agent not found in customer.py")
        
        customer_version = user_agent_match.group(1)
        self.assertEqual(
            customer_version,
            self.expected_version,
            f"customer.py User-Agent version ({customer_version}) doesn't match __init__.py version ({self.expected_version})"
        )

    def test_flask_example_version(self):
        """Test that flask example contains the correct version."""
        flask_path = self.project_root / "examples" / "flask_integration.py"
        if flask_path.exists():
            content = flask_path.read_text()
            
            version_match = re.search(r'"sdk_version": "([^"]+)"', content)
            self.assertIsNotNone(version_match, "sdk_version not found in flask_integration.py")
            
            flask_version = version_match.group(1)
            self.assertEqual(
                flask_version,
                self.expected_version,
                f"flask_integration.py sdk_version ({flask_version}) doesn't match __init__.py version ({self.expected_version})"
            )

    def test_all_version_references_consistent(self):
        """Test that all version references in the codebase are consistent."""
        version_files = [
            ("pyproject.toml", r'version = "([^"]+)"'),
            ("setup.py", r'version="([^"]+)"'),
            ("blaaiz/client.py", r'"User-Agent": "Blaaiz-Python-SDK/([^"]+)"'),
            ("blaaiz/services/customer.py", r'"User-Agent": "Blaaiz-Python-SDK/([^"]+)"'),
            ("examples/flask_integration.py", r'"sdk_version": "([^"]+)"'),
        ]
        
        inconsistent_files = []
        
        for file_path, pattern in version_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                match = re.search(pattern, content)
                if match:
                    version = match.group(1)
                    if version != self.expected_version:
                        inconsistent_files.append(f"{file_path}: {version}")
        
        if inconsistent_files:
            self.fail(
                f"Version inconsistencies found (expected {self.expected_version}):\n" +
                "\n".join(inconsistent_files)
            )


if __name__ == "__main__":
    unittest.main()