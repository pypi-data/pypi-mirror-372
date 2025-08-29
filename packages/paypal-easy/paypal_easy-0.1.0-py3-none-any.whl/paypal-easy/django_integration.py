# paypal_easy/django_integration.py
"""
Optional Django integration helpers
"""
try:
    from django.conf import settings
    from django.http import JsonResponse
    from django.views import View
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

if DJANGO_AVAILABLE:
    class PayPalEasyDjangoMixin:
        """
        Mixin for Django views to easily integrate PayPal
        """
        
        def get_paypal_client(self):
            """Get configured PayPal client from Django settings"""
            client_id = getattr(settings, 'PAYPAL_CLIENT_ID', None)
            client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', None)
            sandbox = getattr(settings, 'PAYPAL_SANDBOX', True)
            
            if not client_id or not client_secret:
                raise ValueError("PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be set in Django settings")
            
            from .client import PayPalEasyClient
            from .enums import Environment
            
            env = Environment.SANDBOX if sandbox else Environment.PRODUCTION
            return PayPalEasyClient(client_id, client_secret, env)
        
        def paypal_success_response(self, order_response):
            """Convert PayPal response to Django JsonResponse"""
            return JsonResponse({
                'success': True,
                'order_id': order_response.id,
                'status': order_response.status.value,
                'approval_url': order_response.approval_url,
                'amount': str(order_response.amount) if order_response.amount else None,
                'currency': order_response.currency.value if order_response.currency else None,
            })
        
        def paypal_error_response(self, error):
            """Convert PayPal error to Django JsonResponse"""
            return JsonResponse({
                'success': False,
                'error': error.message,
                'status_code': error.status_code,
            }, status=400)
