from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


from enum import Enum


class TransactionStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    NOT_RECEIVED = "not_received"
    FAILED = "failed"


class TransactionResponse(BaseModel):
    id: int
    payment_intent_id: str
    amount_received: float
    currency: str
    stripe_payment_status: TransactionStatusEnum
    transaction_id: str
    payment_method: str
    customer_id: Optional[str]
    customer_email: Optional[EmailStr]
    booking_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


class TransactionListResponse(BaseModel):
    payments: List[TransactionResponse]



