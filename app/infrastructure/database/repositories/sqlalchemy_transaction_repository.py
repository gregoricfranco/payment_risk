from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.transaction import Transaction
from app.domain.ports.transaction_repository import DuplicateTransactionError
from app.infrastructure.database.models.transaction_model import TransactionModel


class SqlAlchemyTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, transaction: Transaction) -> Transaction:
        model = TransactionModel(
            id=transaction.id,
            company_id=transaction.company_id,
            external_id=transaction.external_id,
            customer_id=transaction.customer_id,
            amount=transaction.amount,
            currency=transaction.currency,
            payment_method=transaction.payment_method,
            status=transaction.status,
            ip_address=transaction.ip_address,
            device_id=transaction.device_id,
            card_bin=transaction.card_bin,
            card_last_four=transaction.card_last_four,
        )
        self._session.add(model)

        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if _is_duplicate_external_id(exc):
                raise DuplicateTransactionError from exc
            raise

        await self._session.refresh(model)
        return _to_entity(model)


def _is_duplicate_external_id(exc: IntegrityError) -> bool:
    constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    return constraint_name == "uq_transactions_company_external"


def _to_entity(model: TransactionModel) -> Transaction:
    return Transaction(
        id=model.id,
        company_id=model.company_id,
        external_id=model.external_id,
        customer_id=model.customer_id,
        amount=model.amount,
        currency=model.currency,
        payment_method=model.payment_method,
        status=model.status,
        ip_address=str(model.ip_address) if model.ip_address is not None else None,
        device_id=model.device_id,
        card_bin=model.card_bin,
        card_last_four=model.card_last_four,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
