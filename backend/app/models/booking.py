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
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email_address = Column(String(100), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    university = Column(String(100), nullable=False)

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
    payments = relationship("Payment", back_populates="booking")
    stripe_payments = relationship("StripePayment", back_populates="booking")