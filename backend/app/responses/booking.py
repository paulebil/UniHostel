from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import enum

# Enum for Booking Status
class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingResponseSchema(BaseModel):
    id: int

    # Student Information
    first_name: str
    last_email: str
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

