# paypal_easy/client.py
"""
Main client for PayPal Easy
"""
import logging
from typing import Optional, Union
from decimal import Decimal

# PayPal SDK imports
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.configuration import Environment as PayPalEnvironment
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.models.order_request import OrderRequest

from .models import PayPalOrder, PayPalOrderResponse, PayPalError
from .enums import Environment, Currency, OrderIntent

logger = logging.getLogger(__name__)

class PayPalEasyClient:
    """
    Simplified PayPal client that wraps the official SDK
    """
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        environment: Environment = Environment.SANDBOX
    ):
        """
        Initialize PayPal Easy client
        
        Args:
            client_id: PayPal application client ID
            client_secret: PayPal application client secret
            environment: Sandbox or Production
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment
        
        # Map our enum to PayPal SDK enum
        paypal_env = PayPalEnvironment.SANDBOX if environment == Environment.SANDBOX else PayPalEnvironment.PRODUCTION
        
        # Create credentials
        credentials = ClientCredentialsAuthCredentials(
            o_auth_client_id=client_id,
            o_auth_client_secret=client_secret
        )
        
        # Initialize PayPal client
        self.client = PaypalServersdkClient(
            environment=paypal_env,
            client_credentials_auth_credentials=credentials
        )
        
        logger.info(f"PayPal Easy client initialized for {environment.value}")
    
    def create_order(self, amount, currency=Currency.USD, description="", return_url="", cancel_url="", brand_name=""):
        try:
            from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
            from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
            from paypalserversdk.models.order_request import OrderRequest
            
            # Convert amount to string
            amount_str = str(amount)
            
            # Create amount with breakdown
            amount_with_breakdown = AmountWithBreakdown(
                currency_code=currency.value,
                value=amount_str
            )
            
            # Create purchase unit request  
            purchase_unit_request = PurchaseUnitRequest(
                amount=amount_with_breakdown,
                description=description
            )
            
            # Create order request
            order_request = OrderRequest(
                intent="CAPTURE",  # Use string instead of enum
                purchase_units=[purchase_unit_request],
                payment_source={
                    "paypal": {
                        "experience_context": {
                            "return_url": return_url,
                            "cancel_url": cancel_url,
                            "shipping_preference": "NO_SHIPPING",
                            "user_action": "PAY_NOW",
                            "landing_page": "LOGIN",
                            "brand_name": brand_name or "PayPal Easy Demo"
                        }
                    }
                } if return_url and cancel_url else None
            )
            
            # Make API call
            response = self.client.orders.create_order({
                'body': order_request
            })
            
            # Check for success (200 or 201 are both success)
            if response.status_code in [200, 201]:
                order = response.body
                approval_url = None
                
                # Extract approval URL from links
                if hasattr(order, 'links') and order.links:
                    for link in order.links:
                        if hasattr(link, 'rel') and link.rel == "approve":
                            approval_url = getattr(link, 'href', None)
                            break
                
                from .models import PayPalOrderResponse
                from .enums import OrderStatus
                
                return PayPalOrderResponse(
                    id=order.id,
                    status=OrderStatus(order.status),
                    approval_url=approval_url
                )
            else:
                from .models import PayPalError
                return PayPalError(
                    message=f"Order creation failed with status {response.status_code}",
                    status_code=response.status_code
                )
                
        except Exception as e:
            return PayPalError(message=str(e))
    
    
    def get_order(self, order_id: str) -> Union[PayPalOrderResponse, PayPalError]:
        """
        Get order details by ID
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            PayPalOrderResponse on success, PayPalError on failure
        """
        try:
            response = self.client.orders.get_order({
                'id': order_id
            })
            
            if response.status_code == 200:
                logger.info(f"Retrieved PayPal order: {order_id}")
                return PayPalOrderResponse.from_paypal_response(response.body)
            else:
                logger.error(f"Failed to get PayPal order {order_id}: {response.status_code}")
                return PayPalError(
                    message=f"Failed to get order: {response.status_code}",
                    status_code=response.status_code
                )
                
        except Exception as e:
            logger.error(f"Error getting PayPal order {order_id}: {str(e)}")
            return PayPalError(
                message=f"Get order error: {str(e)}"
            )
    
    def capture_order(self, order_id: str) -> Union[PayPalOrderResponse, PayPalError]:
        """
        Capture an approved order
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            PayPalOrderResponse on success, PayPalError on failure
        """
        try:
            # First check order status
            order_response = self.get_order(order_id)
            if isinstance(order_response, PayPalError):
                return order_response
            
            # If already completed, return current status
            if order_response.status == OrderStatus.COMPLETED:
                return order_response
            
            # If approved, capture it
            if order_response.status == OrderStatus.APPROVED:
                response = self.client.orders.capture_order({
                    'id': order_id
                })
                
                if response.status_code == 201:
                    logger.info(f"PayPal order captured: {order_id}")
                    return PayPalOrderResponse.from_paypal_response(response.body)
                else:
                    logger.error(f"PayPal order capture failed: {response.status_code}")
                    return PayPalError(
                        message=f"Order capture failed: {response.status_code}",
                        status_code=response.status_code
                    )
            else:
                return PayPalError(
                    message=f"Order status is {order_response.status.value}, cannot capture"
                )
                
        except Exception as e:
            logger.error(f"Error capturing PayPal order {order_id}: {str(e)}")
            return PayPalError(
                message=f"Capture error: {str(e)}"
            )
