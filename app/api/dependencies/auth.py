from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.authenticate_api_key import AuthenticateApiKey
from app.domain.ports.api_key_repository import ApiKeyRepository
from app.infrastructure.database.repositories.sqlalchemy_api_key_repository import (
    SqlAlchemyApiKeyRepository,
)
from app.infrastructure.database.session import get_db_session


def get_api_key_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiKeyRepository:
    return SqlAlchemyApiKeyRepository(session)


async def get_authenticated_company_id(
    repository: Annotated[ApiKeyRepository, Depends(get_api_key_repository)],
    api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> UUID:
    if not api_key:
        raise _unauthorized()

    company_id = await AuthenticateApiKey(repository).execute(api_key)
    if company_id is None:
        raise _unauthorized()

    return company_id


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )
