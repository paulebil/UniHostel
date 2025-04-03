from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.payments import Payment


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def make_payment(self, payment: Payment):
        try:
            self.session.add(payment)
            self.session.commit()
            self.session.refresh(payment)
            return payment.id
        except IntegrityError:
            self.session.rollback()
            raise

    def update_payment(self, payment: Payment):
        try:
            self.session.merge(payment)
            self.session.commit()
            self.session.refresh(payment)
            return payment.id
        except IntegrityError:
            self.session.rollback()
            raise

    def get_payment_by_id(self, payment_id: int) -> Payment:
        return self.session.query(Payment).filter(Payment.id == payment_id).first()

    def get_payment_by_transaction_id(self, transaction_id: str) -> Payment:
        return self.session.query(Payment).filter(Payment.transaction_id == transaction_id).first()

    def get_payment_by_booking_id(self, booking_id: int) -> Payment:
        return self.session.query(Payment).filter(Payment.booking_id == booking_id).first()