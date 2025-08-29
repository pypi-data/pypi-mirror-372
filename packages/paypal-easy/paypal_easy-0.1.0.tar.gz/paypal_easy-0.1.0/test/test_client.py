import pytest
from decimal import Decimal
from paypal_easy import PayPalEasyClient, Environment, Currency
from paypal_easy.models import PayPalError

def test_client_init():
    client = PayPalEasyClient("test_id", "test_secret", Environment.SANDBOX)
    assert client.client_id == "test_id"
    assert client.environment == Environment.SANDBOX

def test_client_init_production():
    client = PayPalEasyClient("test_id", "test_secret", Environment.PRODUCTION)
    assert client.environment == Environment.PRODUCTION