import pytest
from paypal_easy import PayPalEasyClient, Environment
from paypal_easy.models import PayPalOrder, PayPalError

def test_client_initialization():
    client = PayPalEasyClient("test_id", "test_secret", Environment.SANDBOX)
    assert client.client_id == "test_id"
    assert client.environment == Environment.SANDBOX

def test_paypal_order_model():
    order = PayPalOrder(amount=29.99)
    order_dict = order.to_paypal_dict()
    assert order_dict["intent"] == "CAPTURE"
    assert order_dict["purchase_units"][0]["amount"]["value"] == "29.99"