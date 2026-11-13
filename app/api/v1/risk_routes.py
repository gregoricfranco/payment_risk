from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_authenticated_company_id

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/test")
async def test_authentication(
    company_id: Annotated[UUID, Depends(get_authenticated_company_id)],
) -> dict[str, bool | UUID]:
    return {"authenticated": True, "company_id": company_id}
