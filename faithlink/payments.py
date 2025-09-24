import requests
from django.conf import settings

# 🔹 GCash / PayMongo
def create_paymongo_payment(amount, description="Donation", channel="gcash"):
    url = "https://api.paymongo.com/v1/checkout_sessions"
    headers = {
        "Authorization": f"Basic {settings.PAYMONGO_SECRET_KEY.encode('ascii').hex()}",
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "attributes": {
                "amount": int(float(amount) * 100),  # cents
                "currency": "PHP",
                "description": description,
                "line_items": [
                    {
                        "name": description,
                        "amount": int(float(amount) * 100),
                        "currency": "PHP",
                        "quantity": 1,
                    }
                ],
                "payment_method_types": [channel],
                "success_url": "https://dFaithlink.com/payment-success/",
                "cancel_url": "https://dFaithlink.com/payment-cancel/"
            }
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 🔹 PayPal
def get_paypal_access_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    response = requests.post(
        url,
        headers={"Accept": "application/json"},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    )
    return response.json()["access_token"]

def create_paypal_order(amount, description="Donation"):
    token = get_paypal_access_token()
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {"amount": {"currency_code": "PHP", "value": str(amount)}, "description": description}
        ],
        "application_context": {
            "return_url": "https://dFaithlink.com/payment-success/",
            "cancel_url": "https://dFaithlink.com/payment-cancel/"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
