from pydantic import BaseModel
import enum
from typing import Optional
from datetime import datetime
from typing import List

class PaymentStatus(enum.Enum):
    PENDING="PENDING"
    COMPLETED="COMPLETED"
    NOT_RECEIVED="NOT_RECEIVED"
    FAILED="FAILED"

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Optional[float]
    payment_status: PaymentStatus
    transaction_id: str
    payment_method: str
    created_at: datetime
    updated_at: datetime

class AllPaymentResponse(PaymentResponse):
    payments = List[PaymentResponse]