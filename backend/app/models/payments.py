import enum

from sqlalchemy import Column, Integer, String, DateTime,Enum, ForeignKey, Float
from sqlalchemy.sql import func

from backend.app.database.database import Base

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    NOT_RECEIVED = "not_received"
    FAILED = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    transaction_id = Column(String(100), nullable=False, unique=True, index=True)
    payment_method = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())