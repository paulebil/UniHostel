from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from enum import Enum

class TransactionStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    NOT_RECEIVED = "not_received"
    FAILED = "failed"


class TransactionCreate(BaseModel):
    payment_intent_id: str  # Stripe PaymentIntent ID
    amount_received: float
    currency: str  # e.g., 'usd'
    stripe_payment_status: TransactionStatusEnum
    transaction_id: str  # Stripe charge ID or transaction ID
    payment_method: str
    customer_id: Optional[str] = None  # Stripe Customer ID (if applicable)
    customer_email: Optional[EmailStr] = None  # Customer email (validated as an email)
    booking_id: Optional[int] = None  # Related booking ID


class TransactionUpdate(BaseModel):
    stripe_payment_status: Optional[TransactionStatusEnum] = None
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None
    customer_email: Optional[EmailStr] = None


