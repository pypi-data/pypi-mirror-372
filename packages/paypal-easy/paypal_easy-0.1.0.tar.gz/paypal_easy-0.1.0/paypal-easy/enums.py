# paypal_easy/enums.py
"""
Enums and constants for PayPal Easy
"""
from enum import Enum

class Environment(Enum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    ZAR = "ZAR"  # South African Rand
    # Add more as needed

class OrderIntent(Enum):
    CAPTURE = "CAPTURE"
    AUTHORIZE = "AUTHORIZE"

class OrderStatus(Enum):
    CREATED = "CREATED"
    SAVED = "SAVED"
    APPROVED = "APPROVED"
    VOIDED = "VOIDED"
    COMPLETED = "COMPLETED"
    PAYER_ACTION_REQUIRED = "PAYER_ACTION_REQUIRED"
