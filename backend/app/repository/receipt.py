from backend.app.models.receipt import Receipt

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class ReceiptRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_receipt_metadata(self, receipt: Receipt):
        try:
            self.session.add(receipt)
            self.session.commit()
            self.session.refresh(receipt)
            return receipt.id
        except IntegrityError:
            self.session.rollback()
            raise

    def update_receipt_metadata(self, receipt: Receipt):
        try:
            self.session.merge(receipt)
            self.session.commit()
            self.session.refresh(receipt)
        except IntegrityError:
            self.session.rollback()
            raise

    def get_receipt_metadata_by_id(self, receipt_id: int) -> Receipt:
        return self.session.query(Receipt).filter(Receipt.id == receipt_id).first()