from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_authenticated_company_id
from app.api.schemas.transaction_request import TransactionRequest, TransactionResponse
from app.application.use_cases.register_transaction import (
    RegisterTransaction,
    RegisterTransactionCommand,
)
from app.domain.ports.transaction_repository import (
    DuplicateTransactionError,
    TransactionRepository,
)
from app.infrastructure.database.repositories.sqlalchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)
from app.infrastructure.database.session import get_db_session

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_transaction_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TransactionRepository:
    return SqlAlchemyTransactionRepository(session)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionRequest,
    company_id: Annotated[UUID, Depends(get_authenticated_company_id)],
    repository: Annotated[TransactionRepository, Depends(get_transaction_repository)],
) -> TransactionResponse:
    use_case = RegisterTransaction(repository)
    command = RegisterTransactionCommand(
        company_id=company_id,
        external_id=payload.external_id,
        customer_id=payload.customer_id,
        amount=payload.amount,
        currency=payload.currency,
        payment_method=payload.payment_method,
        status=payload.status,
        ip_address=str(payload.ip_address) if payload.ip_address is not None else None,
        device_id=payload.device_id,
        card_bin=payload.card_bin,
        card_last_four=payload.card_last_four,
    )

    try:
        transaction = await use_case.execute(command)
    except DuplicateTransactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A transaction with this external_id already exists",
        ) from exc

    return TransactionResponse.model_validate(transaction, from_attributes=True)
