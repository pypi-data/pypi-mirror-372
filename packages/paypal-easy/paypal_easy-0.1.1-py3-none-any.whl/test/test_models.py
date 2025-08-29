from decimal import Decimal
from paypal_easy.models import PayPalOrder
from paypal_easy.enums import Currency, OrderIntent

def test_order_creation():
    order = PayPalOrder(amount=Decimal("29.99"))
    assert order.amount == Decimal("29.99")
    assert order.currency == Currency.USD

def test_order_to_dict():
    order = PayPalOrder(
        amount=Decimal("100.00"),
        currency=Currency.EUR,
        description="Test order"
    )
    result = order.to_paypal_dict()
    assert result["intent"] == "CAPTURE"
    assert result["purchase_units"][0]["amount"]["value"] == "100.00"
    assert result["purchase_units"][0]["amount"]["currency_code"] == "EUR"