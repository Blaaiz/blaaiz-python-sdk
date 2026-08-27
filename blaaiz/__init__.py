"""
Blaaiz Python SDK

A comprehensive Python SDK for the Blaaiz RaaS (Remittance as a Service) API.
"""

from .client import BlaaizAPIClient, ALL_SCOPES
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
    RateService,
    SwapService,
    RefundService,
)

__version__ = "1.2.0"
__author__ = "Blaaiz Team"
__email__ = "onboarding@blaaiz.com"

__all__ = [
    "Blaaiz",
    "BlaaizError",
    "BlaaizAPIClient",
    "ALL_SCOPES",
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
    "RateService",
    "SwapService",
    "RefundService",
]
