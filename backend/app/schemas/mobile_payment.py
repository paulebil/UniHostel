from pydantic import BaseModel, Field, constr
from typing import Optional, Literal
from enum import Enum
from datetime import datetime


# Enums for consistency with the model
class PaymentMethod(str, Enum):
    card = "card"
    mobile_money = "mobile_money"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


# Sub-schemas for conditional fields
class CardDetails(BaseModel):
    card_number: constr(min_length=12, max_length=19)
    expiry_date: str  # Format: MM/YY or MM/YYYY
    cvc: constr(min_length=3, max_length=4)
    name_on_card: str


class MobileMoneyDetails(BaseModel):
    provider: str
    phone_number: constr(min_length=10, max_length=20)
    account_name: str


# Main creation schema
class PaymentCreate(BaseModel):
    hostel_id: int
    room_id: int
    amount: float
    payment_method: PaymentMethod
    card_details: Optional[CardDetails] = None
    mobile_money_details: Optional[MobileMoneyDetails] = None


# Response schema
class PaymentResponse(BaseModel):
    id: int
    hostel_id: int
    room_id: int
    amount: float
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: str

    card_number: Optional[str] = None
    expiry_date: Optional[str] = None
    name_on_card: Optional[str] = None

    provider: Optional[str] = None
    phone_number: Optional[str] = None
    account_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
