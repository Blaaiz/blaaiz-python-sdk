#!/usr/bin/env python3
"""
Script to update version numbers across all files in the project.
Usage: python update_version.py 1.0.3
"""

import re
import sys
from pathlib import Path


def update_version(new_version: str) -> None:
    """Update version numbers in all relevant files."""

    # Validate version format
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print(f"Error: Invalid version format '{new_version}'. Expected format: X.Y.Z")
        sys.exit(1)

    project_root = Path(__file__).parent

    # Files to update with their patterns
    version_updates = [
        {
            "file": "pyproject.toml",
            "pattern": r'(^version = ")[^"]+(")',
            "replacement": f"\\g<1>{new_version}\\g<2>",
        },
        {
            "file": "blaaiz/__init__.py",
            "pattern": r'__version__ = "[^"]+"',
            "replacement": f'__version__ = "{new_version}"',
        },
        {
            "file": "setup.py",
            "pattern": r'version="[^"]+"',
            "replacement": f'version="{new_version}"',
        },
        {
            "file": "blaaiz/client.py",
            "pattern": r'"User-Agent": "Blaaiz-Python-SDK/[^"]+"',
            "replacement": f'"User-Agent": "Blaaiz-Python-SDK/{new_version}"',
        },
        {
            "file": "blaaiz/services/customer.py",
            "pattern": r'"User-Agent": "Blaaiz-Python-SDK/[^"]+"',
            "replacement": f'"User-Agent": "Blaaiz-Python-SDK/{new_version}"',
        },
        {
            "file": "examples/flask_integration.py",
            "pattern": r'"sdk_version": "[^"]+"',
            "replacement": f'"sdk_version": "{new_version}"',
        },
    ]

    updated_files = []
    failed_files = []

    for update in version_updates:
        file_path = project_root / update["file"]

        if not file_path.exists():
            print(f"Warning: File {update['file']} does not exist, skipping...")
            continue

        try:
            # Read file content
            content = file_path.read_text()

            # Check if pattern exists
            if not re.search(update["pattern"], content):
                print(f"Warning: Pattern not found in {update['file']}, skipping...")
                continue

            # Replace version
            if update["file"] == "pyproject.toml":
                updated_content = re.sub(
                    update["pattern"], update["replacement"], content, flags=re.MULTILINE
                )
            else:
                updated_content = re.sub(update["pattern"], update["replacement"], content)

            # Write back to file
            file_path.write_text(updated_content)
            updated_files.append(update["file"])

        except Exception as e:
            print(f"Error updating {update['file']}: {e}")
            failed_files.append(update["file"])

    # Print summary
    print(f"\n✅ Successfully updated version to {new_version} in {len(updated_files)} files:")
    for file in updated_files:
        print(f"   - {file}")

    if failed_files:
        print(f"\n❌ Failed to update {len(failed_files)} files:")
        for file in failed_files:
            print(f"   - {file}")

    print(f"\nNext steps:")
    print(
        f"1. Run tests to verify everything works: python -m pytest tests/test_version_consistency.py"
    )
    print(f"2. Build the package: python -m build")
    print(f"3. Upload to PyPI: python -m twine upload dist/blaaiz_python_sdk-{new_version}*")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        print("Example: python update_version.py 1.0.3")
        sys.exit(1)

    new_version = sys.argv[1]
    update_version(new_version)
