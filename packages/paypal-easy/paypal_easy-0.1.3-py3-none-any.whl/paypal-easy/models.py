# paypal_easy/models.py
"""
Data models for PayPal Easy
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from decimal import Decimal
from .enums import Currency, OrderIntent, OrderStatus

@dataclass
class PayPalOrder:
    """Simplified order creation model"""
    amount: Decimal
    currency: Currency = Currency.USD
    intent: OrderIntent = OrderIntent.CAPTURE
    reference_id: Optional[str] = None
    description: Optional[str] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    brand_name: Optional[str] = None
    
    def to_paypal_dict(self) -> Dict[str, Any]:
        """Convert to PayPal SDK format"""
        purchase_unit = {
            "amount": {
                "currency_code": self.currency.value,
                "value": str(self.amount)
            }
        }
        
        if self.reference_id:
            purchase_unit["reference_id"] = self.reference_id
            
        if self.description:
            purchase_unit["description"] = self.description
        
        order_dict = {
            "intent": self.intent.value,
            "purchase_units": [purchase_unit]
        }
        
        # Add PayPal wallet experience context if URLs provided
        if self.return_url and self.cancel_url:
            order_dict["payment_source"] = {
                "paypal": {
                    "experience_context": {
                        "return_url": self.return_url,
                        "cancel_url": self.cancel_url,
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "landing_page": "LOGIN"
                    }
                }
            }
            
            if self.brand_name:
                order_dict["payment_source"]["paypal"]["experience_context"]["brand_name"] = self.brand_name
        
        return order_dict

@dataclass
class PayPalOrderResponse:
    """Simplified order response model"""
    id: str
    status: OrderStatus
    approval_url: Optional[str] = None
    payer_email: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[Currency] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_paypal_response(cls, response_body) -> 'PayPalOrderResponse':
        """Create from PayPal SDK response"""
        approval_url = None
        
        # Extract approval URL from HATEOAS links
        if hasattr(response_body, 'links') and response_body.links:
            for link in response_body.links:
                if hasattr(link, 'rel') and link.rel == "approve":
                    approval_url = getattr(link, 'href', None)
                    break
        
        # Extract payer info
        payer_email = None
        if hasattr(response_body, 'payer') and hasattr(response_body.payer, 'email_address'):
            payer_email = response_body.payer.email_address
        
        # Extract amount info
        amount = None
        currency = None
        if (hasattr(response_body, 'purchase_units') and 
            response_body.purchase_units and 
            hasattr(response_body.purchase_units[0], 'amount')):
            amount_obj = response_body.purchase_units[0].amount
            if hasattr(amount_obj, 'value'):
                amount = Decimal(amount_obj.value)
            if hasattr(amount_obj, 'currency_code'):
                try:
                    currency = Currency(amount_obj.currency_code)
                except ValueError:
                    pass  # Unknown currency
        
        return cls(
            id=response_body.id,
            status=OrderStatus(response_body.status),
            approval_url=approval_url,
            payer_email=payer_email,
            amount=amount,
            currency=currency,
            raw_response=response_body.__dict__ if hasattr(response_body, '__dict__') else None
        )

@dataclass
class PayPalError:
    """Simplified error model"""
    message: str
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
