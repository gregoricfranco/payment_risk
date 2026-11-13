from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.entities.transaction import Transaction
from app.domain.ports.transaction_repository import TransactionRepository


@dataclass(frozen=True, slots=True)
class RegisterTransactionCommand:
    company_id: UUID
    external_id: str
    customer_id: str
    amount: Decimal
    currency: str
    payment_method: str
    status: str
    ip_address: str | None
    device_id: str | None
    card_bin: str | None
    card_last_four: str | None


class RegisterTransaction:
    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    async def execute(self, command: RegisterTransactionCommand) -> Transaction:
        transaction = Transaction(
            id=uuid4(),
            company_id=command.company_id,
            external_id=command.external_id,
            customer_id=command.customer_id,
            amount=command.amount,
            currency=command.currency,
            payment_method=command.payment_method,
            status=command.status,
            ip_address=command.ip_address,
            device_id=command.device_id,
            card_bin=command.card_bin,
            card_last_four=command.card_last_four,
        )
        return await self._repository.create(transaction)
