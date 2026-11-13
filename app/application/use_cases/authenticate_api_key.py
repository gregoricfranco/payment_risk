import hashlib
from uuid import UUID

from app.domain.ports.api_key_repository import ApiKeyRepository


class AuthenticateApiKey:
    def __init__(self, repository: ApiKeyRepository) -> None:
        self._repository = repository

    async def execute(self, api_key: str) -> UUID | None:
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        return await self._repository.find_active_company_id_by_hash(key_hash)
