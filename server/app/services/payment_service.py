import requests
import stripe
from ..config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

CHAPA_BASE_URL = "https://api.chapa.co/v1"

def initiate_chapa_payment(
    amount: float,
    email: str,
    first_name: str,
    tx_ref: str,
    course_title: str,
    callback_url: str
) -> dict:
    """
    Start a Chapa payment.
    Returns checkout_url where user completes payment.
    tx_ref is our unique transaction reference to track this payment.
    """
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": first_name[:50],
        "last_name": "User",
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": f"{settings.FRONTEND_URL}/payment/success",
        "customization": {
            "title": course_title[:16],  # Chapa limits to 16 chars
            "description": f"Course payment"
        }
    }
    response = requests.post(
        f"{CHAPA_BASE_URL}/transaction/initialize",
        json=payload,
        headers=headers
    )
    return response.json()

def verify_chapa_payment(tx_ref: str) -> dict:
    """
    Verify a Chapa payment using the transaction reference.
    Called when Chapa sends a webhook or user returns from payment page.
    """
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }
    response = requests.get(
        f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}",
        headers=headers
    )
    return response.json()

def initiate_stripe_payment(
    amount: float,
    course_title: str,
    course_id: int,
    user_id: int
) -> dict:
    """
    Start a Stripe payment session.
    Returns checkout_url where user completes payment.
    amount is in USD.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": course_title,
                },
                "unit_amount": int(amount * 100),  # Stripe uses cents
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
        metadata={
            "course_id": course_id,
            "user_id": user_id
        }
    )
    return {"checkout_url": session.url, "session_id": session.id}
