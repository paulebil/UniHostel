import enum

from sqlalchemy import Column, Integer, String, DateTime,Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
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

class StripePaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    NOT_RECEIVED = "not_received"
    FAILED = "failed"

class StripePayment(Base):
    __tablename__ = "stripe_payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_intent_id = Column(String(100), nullable=False, unique=True)  # Stripe PaymentIntent ID
    amount_received = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # e.g., 'usd'
    stripe_payment_status = Column(Enum(StripePaymentStatus), nullable=False, default=StripePaymentStatus.PENDING)
    transaction_id = Column(String(100), nullable=False)  # Stripe charge ID or transaction ID
    payment_method = Column(String(100), nullable=False)
    customer_id = Column(String(100), nullable=True)  # Stripe Customer ID (if applicable)
    customer_email = Column(String(100), nullable=True)  # Customer email
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships if needed
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    booking = relationship("Booking", back_populates="payments")

    def __repr__(self):
        return f"<StripePayment(id={self.id}, payment_intent_id={self.payment_intent_id}, status={self.payment_status})>"