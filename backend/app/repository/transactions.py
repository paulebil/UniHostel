from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.payments import StripePayment


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_transaction(self, transaction: StripePayment):
        try:
            self.session.add(transaction)
            self.session.commit()
            self.session.refresh(transaction)
        except IntegrityError:
            self.session.rollback()
            raise

    def get_transaction_by_id(self, transaction_id: str) -> StripePayment:
        return self.session.query(StripePayment).filter(StripePayment.transaction_id  == transaction_id).first()

