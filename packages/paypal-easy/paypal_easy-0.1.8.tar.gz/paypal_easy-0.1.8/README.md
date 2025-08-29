# README.md
# PayPal Easy

A simplified, developer-friendly wrapper around PayPal's Python Server SDK.

## Why PayPal Easy?

PayPal's official Python SDK can be challenging to work with due to:
- Missing or inconsistent class imports
- Complex parameter structures
- Inconsistent documentation
- Verbose API calls

PayPal Easy solves these problems by providing:
- ✅ Clean, consistent API
- ✅ Proper error handling
- ✅ Type hints and IDE support
- ✅ Simplified method signatures
- ✅ Django integration helpers

## Demo

Here is a sample Django project that implements paypal-easy

https://github.com/doculearn/paypal-easy-demo

## Video Walkthrough

<a href="https://youtu.be/EMO9o9O4Fh4?si=5kgIg6Rlbwljzs_W">Watch on Youtube</a>

## Installation

```bash
pip install paypal-easy
```

## Quick Start

```python
from paypal_easy import PayPalEasyClient, Environment, Currency
from decimal import Decimal

# Initialize client
client = PayPalEasyClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    environment=Environment.SANDBOX
)

# Create an order
result = client.create_order(
    amount=Decimal("29.99"),
    currency=Currency.USD,
    description="Premium subscription",
    return_url="https://yoursite.com/success",
    cancel_url="https://yoursite.com/cancel"
)

if hasattr(result, 'id'):  # Success
    print(f"Order created: {result.id}")
    print(f"Approval URL: {result.approval_url}")
else:  # Error
    print(f"Error: {result.message}")
```

## Django Integration

```python
# views.py
from paypal_easy.django_integration import PayPalEasyDjangoMixin
from django.views import View

class CreatePaymentView(PayPalEasyDjangoMixin, View):
    def post(self, request):
        client = self.get_paypal_client()
        
        result = client.create_order(
            amount=request.POST.get('amount'),
            description="Order payment"
        )
        
        if hasattr(result, 'id'):
            return self.paypal_success_response(result)
        else:
            return self.paypal_error_response(result)
```

## Features

- **Simple Order Creation**: Create orders with minimal code
- **Automatic URL Handling**: Easy approval flow setup
- **Error Handling**: Consistent error responses
- **Django Integration**: Ready-to-use Django mixins
- **Type Safety**: Full type hints for better IDE support
- **Logging**: Built-in logging for debugging

## Comparison

### Before (Official SDK)
```python
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.configuration import Environment
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.models.order_request import OrderRequest

credentials = ClientCredentialsAuthCredentials(
    o_auth_client_id=client_id,
    o_auth_client_secret=client_secret
)

client = PaypalServersdkClient(
    environment=Environment.SANDBOX,
    client_credentials_auth_credentials=credentials
)

order_request = OrderRequest({
    "intent": "CAPTURE",
    "purchase_units": [{
        "amount": {
            "currency_code": "USD", 
            "value": "29.99"
        }
    }]
})

response = client.orders.create_order({'body': order_request})
```

### After (PayPal Easy)
```python
from paypal_easy import PayPalEasyClient, Environment, Currency

client = PayPalEasyClient(client_id, client_secret, Environment.SANDBOX)
result = client.create_order(amount="29.99", currency=Currency.USD)
```

## Contributing

Contributions welcome! Please feel free to submit issues and enhancement requests.

### Donations 

Would you like to support the work we do?

Click Here to Donate - <a href="https://www.paypal.com/donate/?hosted_button_id=L7VG622B9XESL" target="_blank">Donate Link</a>

## License

MIT License - see LICENSE file for details.

## Maintainers

William Mabotja - <a href="https://williammabotja.xyz">Portfolio Site</a>