from pydantic import BaseModel
import enum
from typing import Optional

class PaymentStatus(enum.Enum):
    PENDING="PENDING"
    COMPLETED="COMPLETED"
    NOT_RECEIVED="NOT_RECEIVED"
    FAILED="FAILED"

class PaymentCreate(BaseModel):
    booking_id: int
    amount: Optional[float]
    payment_status: PaymentStatus
    transaction_id: str
    payment_method: str

class PaymentUpdate(BaseModel):
    amount: Optional[float]
    payment_status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None