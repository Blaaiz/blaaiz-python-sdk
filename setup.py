"""
Setup configuration for blaaiz-python-sdk
"""

from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="blaaiz-python-sdk",
    version="1.0.0",
    author="Blaaiz Team",
    author_email="onboarding@blaaiz.com",
    description="A comprehensive Python SDK for the Blaaiz RaaS (Remittance as a Service) API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blaaiz/blaaiz-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/blaaiz/blaaiz-python-sdk/issues",
        "Documentation": "https://docs.business.blaaiz.com",
        "Source Code": "https://github.com/blaaiz/blaaiz-python-sdk",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0",
            "wheel>=0.36",
        ],
    },
    keywords="blaaiz remittance payment fintech api sdk",
    include_package_data=True,
    zip_safe=False,
)