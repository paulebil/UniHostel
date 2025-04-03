from fastapi import HTTPException, status

from backend.app.repository.transactions import TransactionRepository
from backend.app.schemas.transactions import *
from backend.app.responses.transactions import *


class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    async def create_transaction(self, data:TransactionCreate):
        pass