from pydantic import BaseModel,constr
from typing import Optional
import enum


# Enum for Booking Status
class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


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
    #status: BookingStatus = BookingStatus.PENDING


class BookingUpdateSchema(BaseModel):
    # Booking ID (Required for identification)
    booking_id: int

    # Student Information (Optional to update)
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    student_phone: Optional[constr(min_length=10, max_length=20)] = None
    student_university: Optional[str] = None
    student_course: Optional[str] = None
    student_study_year: Optional[str] = None

    # Home residence information (Optional to update)
    home_address: Optional[str] = None
    home_district: Optional[str] = None
    home_country: Optional[str] = None

    # Next of Kin Information (Optional to update)
    next_of_kin_name: Optional[str] = None
    next_of_kin_phone: Optional[constr(min_length=10, max_length=20)] = None
    kin_relationship: Optional[str] = None

    # Foreign Keys (either hostel_id or room_id will be set, Optional)
    hostel_id: Optional[int] = None
    room_id: Optional[int] = None

    # Booking Status (Optional to update, if needed in future)
    #status: Optional[BookingStatus] = None
