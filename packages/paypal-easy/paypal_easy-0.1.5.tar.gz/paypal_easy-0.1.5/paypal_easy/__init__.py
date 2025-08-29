# paypal_easy/__init__.py
"""
PayPal Easy - A simplified wrapper for PayPal's Python Server SDK

This package provides a clean, consistent interface to PayPal's payment APIs,
addressing common issues with the official SDK.
"""

from .client import PayPalEasyClient
from .models import PayPalOrder, PayPalOrderResponse, PayPalError
from .enums import Environment, Currency, OrderIntent, OrderStatus

__version__ = "0.1.0"
__all__ = [
    "PayPalEasyClient", 
    "PayPalOrder", 
    "PayPalOrderResponse", 
    "PayPalError",
    "Environment", 
    "Currency", 
    "OrderIntent", 
    "OrderStatus"
]