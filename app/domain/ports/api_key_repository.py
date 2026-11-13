from typing import Protocol
from uuid import UUID


class ApiKeyRepository(Protocol):
    async def find_active_company_id_by_hash(self, key_hash: str) -> UUID | None: ...
