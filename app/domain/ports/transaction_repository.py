from typing import Protocol

from app.domain.entities.transaction import Transaction


class DuplicateTransactionError(Exception):
    """Raised when an external transaction ID already exists for a company."""


class TransactionRepository(Protocol):
    async def create(self, transaction: Transaction) -> Transaction: ...
