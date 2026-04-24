from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentInitiate(BaseModel):
    course_id:int
    # Country is taken from user profile automatically

class PaymentResponse(BaseModel):
    payment_id: int
    course_id: int
    amount: float
    provider: str           # "chapa" or "stripe"
    status: str             # "pending", "completed", "failed"
    checkout_url: str       # URL to redirect user to payment page
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentStatusResponse(BaseModel):
    payment_id: int
    status: str
    provider: str
    amount: float
    transaction_id: Optional[str] = None