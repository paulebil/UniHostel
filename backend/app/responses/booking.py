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
    student_name: str
    student_email: str
    student_phone: str
    student_university: str
    student_course: str
    student_study_year: str

    # Home residence information
    home_address: str
    home_district: str
    home_country: str

    # Next of Kin Information
    next_of_kin_name: str
    next_of_kin_phone: str
    kin_relationship: str

    # Foreign Keys (either hostel_id or room_id will be set)
    hostel_id: Optional[int] = None
    room_id: Optional[int] = None

    # Booking Status
    status: BookingStatus

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

