"""
Blaaiz Python SDK

A comprehensive Python SDK for the Blaaiz RaaS (Remittance as a Service) API.
"""

from .client import BlaaizAPIClient
from .error import BlaaizError
from .blaaiz import Blaaiz
from .services import (
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

__version__ = "1.0.0"
__author__ = "Blaaiz Team"
__email__ = "onboarding@blaaiz.com"

__all__ = [
    "Blaaiz",
    "BlaaizError",
    "BlaaizAPIClient",
    "CustomerService",
    "CollectionService",
    "PayoutService",
    "WalletService",
    "VirtualBankAccountService",
    "TransactionService",
    "BankService",
    "CurrencyService",
    "FeesService",
    "FileService",
    "WebhookService",
]