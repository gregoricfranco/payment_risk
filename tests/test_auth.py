import hashlib
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_api_key_repository
from app.main import app

COMPANY_ID = UUID("11111111-1111-1111-1111-111111111111")
VALID_API_KEY = "prk_valid_test_key"
VALID_KEY_HASH = hashlib.sha256(VALID_API_KEY.encode("utf-8")).hexdigest()


class InMemoryApiKeyRepository:
    def __init__(self) -> None:
        self.received_hash: str | None = None

    async def find_active_company_id_by_hash(self, key_hash: str) -> UUID | None:
        self.received_hash = key_hash
        return COMPANY_ID if key_hash == VALID_KEY_HASH else None


def test_risk_endpoint_accepts_valid_api_key() -> None:
    repository = InMemoryApiKeyRepository()
    app.dependency_overrides[get_api_key_repository] = lambda: repository

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/risk/test",
                headers={"X-API-Key": VALID_API_KEY},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"authenticated": True, "company_id": str(COMPANY_ID)}
    assert repository.received_hash == VALID_KEY_HASH


def test_risk_endpoint_rejects_invalid_api_key() -> None:
    app.dependency_overrides[get_api_key_repository] = InMemoryApiKeyRepository

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/risk/test",
                headers={"X-API-Key": "invalid"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


def test_risk_endpoint_rejects_missing_api_key() -> None:
    app.dependency_overrides[get_api_key_repository] = InMemoryApiKeyRepository

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/risk/test")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


def test_public_endpoints_do_not_require_api_key() -> None:
    with TestClient(app) as client:
        health_response = client.get("/health")
        docs_response = client.get("/docs")

    assert health_response.status_code == 200
    assert docs_response.status_code == 200
