from fastapi import HTTPException, status

from backend.app.repository.transactions import TransactionRepository
from backend.app.schemas.transactions import *
from backend.app.responses.transactions import *
from backend.app.models.payments import StripePayment


class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    async def create_transaction(self, data:TransactionCreate) -> TransactionResponse:

        # Create transaction
        transaction = StripePayment(
            payment_intent_id=data.payment_intent_id,
            amount_received=data.amount_received,
            currency=data.currency,
            stripe_payment_status=data.stripe_payment_status,
            transaction_id=data.transaction_id,
            payment_method=data.payment_method,
            customer_id=data.customer_id,
            customer_email=data.customer_email,
            booking_id=data.booking_id,

            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        transaction_id = self.transaction_repository.create_transaction(transaction)

        # Build a transaction response model

        transaction = self.transaction_repository.get_transaction_by_id(transaction_id)

        transaction_response = TransactionResponse(
            id=transaction.id,
            payment_intent_id=transaction.payment_intent_id,
            amount_received=transaction.amount_received,
            currency=transaction.currency,
            stripe_payment_status=transaction.stripe_payment_status,
            transaction_id=transaction.transaction_id,
            payment_method=transaction.payment_method,
            customer_id=transaction.customer_id,
            customer_email=transaction.customer_email,
            booking_id=transaction.booking_id,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )

        return transaction_response