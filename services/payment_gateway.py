import requests
from config import ZARINPAL_MERCHANT_ID, ZIBAL_MERCHANT_ID, PAYMENT_CALLBACK_URL
from database.models import PaymentGateway


def create_zarinpal_payment(amount, description):
    url = "https://api.zarinpal.com/pg/v4/payment/request.json"
    data = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "callback_url": PAYMENT_CALLBACK_URL,
        "description": description,
    }
    response = requests.post(url, json=data)
    return response.json()


def verify_zarinpal_payment(authority, amount):
    url = "https://api.zarinpal.com/pg/v4/payment/verify.json"
    data = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "authority": authority,
    }
    response = requests.post(url, json=data)
    return response.json()


def create_zibal_payment(amount, description):
    url = "https://gateway.zibal.ir/v1/request"
    data = {
        "merchant": ZIBAL_MERCHANT_ID,
        "amount": amount,
        "callbackUrl": PAYMENT_CALLBACK_URL,
        "description": description,
    }
    response = requests.post(url, json=data)
    return response.json()


def verify_zibal_payment(trackId):
    url = "https://gateway.zibal.ir/v1/verify"
    data = {
        "merchant": ZIBAL_MERCHANT_ID,
        "trackId": trackId,
    }
    response = requests.post(url, json=data)
    return response.json()


def create_payment(user_id, amount, gateway):
    description = f"Payment for user {user_id}"
    if gateway == PaymentGateway.ZARINPAL:
        payment_data = create_zarinpal_payment(amount, description)
        return f"https://www.zarinpal.com/pg/StartPay/{payment_data['authority']}"
    elif gateway == PaymentGateway.ZIBAL:
        payment_data = create_zibal_payment(amount, description)
        return f"https://gateway.zibal.ir/start/{payment_data['trackId']}"
    else:
        raise ValueError("Invalid payment gateway")


def process_payment(payment_id, gateway, amount):
    if gateway == PaymentGateway.ZARINPAL:
        return verify_zarinpal_payment(payment_id, amount)
    elif gateway == PaymentGateway.ZIBAL:
        return verify_zibal_payment(payment_id)
    else:
        raise ValueError("Invalid payment gateway")
