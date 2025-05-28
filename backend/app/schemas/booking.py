from pydantic import BaseModel,constr
from typing import Optional
import enum
from datetime import datetime

# Enum for Booking Status
class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class BookingCreateSchema(BaseModel):
    # Student Information
    first_name: str
    last_name: str
    email_address: str
    phone_number: str
    university: str

    # Foreign Keys (either hostel_id or room_id will be set)
    hostel_id: Optional[int] = None
    room_id: Optional[int] = None
    # Booking Status
    status: BookingStatus
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

