from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Transaction:
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
    created_at: datetime | None = None
    updated_at: datetime | None = None
