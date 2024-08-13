import requests
from config import ZIBAL_API_KEY, ZARINPAL_API_KEY

class PaymentService:
    def __init__(self):
        self.zibal_api_key = ZIBAL_API_KEY
        self.zarinpal_api_key = ZARINPAL_API_KEY

    def redirect_to_payment_gateway(self, amount):
        # Implementation for redirecting user to payment gateway
        pass