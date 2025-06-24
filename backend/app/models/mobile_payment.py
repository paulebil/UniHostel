from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from enum import Enum as PyEnum


class Base(DeclarativeBase):
    pass


class PaymentMethod(PyEnum):
    CARD = "card"
    MOBILE_MONEY = "mobile_money"


class PaymentStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Incoming from frontend
    hostel_id: Mapped[int] = mapped_column(nullable=False)
    room_id: Mapped[int] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)

    # Dynamic fields depending on payment method
    # Card details
    card_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    expiry_date: Mapped[str | None] = mapped_column(String(7), nullable=True)  # e.g. "06/25"
    cvc: Mapped[str | None] = mapped_column(String(4), nullable=True)
    name_on_card: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Mobile money details
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    account_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Transaction tracking
    transaction_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), nullable=False,
                                                          default=PaymentStatus.PENDING)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    booking = relationship("Booking", back_populates="payments")