from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, field_validator


class TransactionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    external_id: Annotated[str, Field(min_length=1, max_length=100)]
    customer_id: Annotated[str, Field(min_length=1, max_length=100)]
    amount: Annotated[Decimal, Field(gt=0, max_digits=15, decimal_places=2)]
    currency: Annotated[str, Field(min_length=3, max_length=3)]
    payment_method: Annotated[str, Field(min_length=1, max_length=30)]
    status: Annotated[str, Field(min_length=1, max_length=30)] = "pending"
    ip_address: IPvAnyAddress | None = None
    device_id: Annotated[str | None, Field(max_length=100)] = None
    card_bin: Annotated[str | None, Field(pattern=r"^\d{6,8}$")] = None
    card_last_four: Annotated[str | None, Field(pattern=r"^\d{4}$")] = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TransactionResponse(BaseModel):
    id: UUID
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
    created_at: datetime
    updated_at: datetime
