from pydantic import BaseModel,constr
from typing import Optional
import enum


# Enum for Booking Status
class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingCreateSchema(BaseModel):
    # Student Information
    student_name: str
    student_email: str
    student_phone: constr(min_length=10, max_length=20)
    student_university: str
    student_course: str
    student_study_year: str

    # Home residence information
    home_address: str
    home_district: str
    home_country: str

    # Next of Kin Information
    next_of_kin_name: str
    next_of_kin_phone: constr(min_length=10, max_length=20)
    kin_relationship: str

    # Foreign Keys (either hostel_id or room_id will be set)
    hostel_id: Optional[int] = None
    room_id: Optional[int] = None

    # Booking Status
    status: BookingStatus = BookingStatus.PENDING


class BookingUpdateSchema(BaseModel):
    # Optional fields to update
    status: Optional[BookingStatus] = None
    room_id: Optional[int] = None
    hostel_id: Optional[int] = None



