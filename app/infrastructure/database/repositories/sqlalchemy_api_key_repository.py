from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.api_key_model import ApiKeyModel
from app.infrastructure.database.models.company_model import CompanyModel


class SqlAlchemyApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_active_company_id_by_hash(self, key_hash: str) -> UUID | None:
        statement = (
            select(ApiKeyModel)
            .join(ApiKeyModel.company)
            .where(
                ApiKeyModel.key_hash == key_hash,
                ApiKeyModel.revoked_at.is_(None),
                (ApiKeyModel.expires_at.is_(None) | (ApiKeyModel.expires_at > func.now())),
                CompanyModel.is_active.is_(True),
            )
        )
        api_key = (await self._session.execute(statement)).scalar_one_or_none()

        if api_key is None:
            return None

        api_key.last_used_at = datetime.now(UTC)
        await self._session.commit()
        return api_key.company_id
