from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from backend.app.database.database import Base
import enum

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Booking(Base):
    """
    Represents a student's hostel booking request.
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Student Information
    student_name = Column(String(100), nullable=False)
    student_email = Column(String(100), nullable=False, index=True)
    student_phone = Column(String(20), nullable=False)
    student_university = Column(String(100), nullable=False)
    student_course = Column(String(100), nullable=False)
    student_study_year = Column(String(50), nullable=False)

    # Home residence information
    home_address = Column(String(100), nullable=False)
    home_district = Column(String(100), nullable=False)
    home_country = Column(String(50), nullable=False)

    # Next of Kin Information
    next_of_kin_name = Column(String(100), nullable=False)
    next_of_kin_phone = Column(String(20), nullable=False)
    kin_relationship = Column(String(50), nullable=False)

    # Foreign Keys (Either hostel_id or room_id will be set)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)

    # Booking Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    hostel = relationship("Hostel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")