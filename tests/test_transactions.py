from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_authenticated_company_id
from app.api.v1.transaction_routes import get_transaction_repository
from app.domain.entities.transaction import Transaction
from app.domain.ports.transaction_repository import DuplicateTransactionError
from app.main import app

COMPANY_ID = UUID("11111111-1111-1111-1111-111111111111")
TRANSACTION_ID = UUID("22222222-2222-2222-2222-222222222222")
PAYLOAD = {
    "external_id": "txn_100001",
    "customer_id": "customer_123",
    "amount": "250.00",
    "currency": "BRL",
    "payment_method": "credit_card",
    "status": "pending",
    "ip_address": "189.45.120.10",
    "device_id": "device_abc123",
    "card_bin": "411111",
    "card_last_four": "1234",
}


async def authenticated_company_override() -> UUID:
    return COMPANY_ID


class InMemoryTransactionRepository:
    async def create(self, transaction: Transaction) -> Transaction:
        timestamp = datetime(2026, 11, 12, tzinfo=UTC)
        return Transaction(
            id=TRANSACTION_ID,
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
            created_at=timestamp,
            updated_at=timestamp,
        )


class DuplicateTransactionRepository:
    async def create(self, transaction: Transaction) -> Transaction:
        raise DuplicateTransactionError


def test_create_transaction() -> None:
    app.dependency_overrides[get_authenticated_company_id] = authenticated_company_override
    app.dependency_overrides[get_transaction_repository] = InMemoryTransactionRepository

    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/transactions", json=PAYLOAD)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["id"] == str(TRANSACTION_ID)
    assert response.json()["company_id"] == str(COMPANY_ID)
    assert response.json()["amount"] == "250.00"


def test_create_transaction_requires_api_key() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/transactions", json=PAYLOAD)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


def test_create_duplicate_transaction() -> None:
    app.dependency_overrides[get_authenticated_company_id] = authenticated_company_override
    app.dependency_overrides[get_transaction_repository] = DuplicateTransactionRepository

    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/transactions", json=PAYLOAD)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "A transaction with this external_id already exists"}
