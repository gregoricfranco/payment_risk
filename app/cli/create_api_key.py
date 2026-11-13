import argparse
import asyncio
import hashlib
import secrets
from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select

from app.infrastructure.database.models.api_key_model import ApiKeyModel
from app.infrastructure.database.models.company_model import CompanyModel
from app.infrastructure.database.session import async_session_factory


@dataclass(frozen=True, slots=True)
class GeneratedApiKey:
    raw_key: str
    prefix: str
    key_hash: str


def generate_api_key() -> GeneratedApiKey:
    raw_key = f"prk_{secrets.token_urlsafe(32)}"
    return GeneratedApiKey(
        raw_key=raw_key,
        prefix=raw_key[:32],
        key_hash=hashlib.sha256(raw_key.encode("utf-8")).hexdigest(),
    )


async def create_api_key(company_id: UUID, name: str) -> GeneratedApiKey:
    async with async_session_factory() as session:
        company = await session.scalar(select(CompanyModel).where(CompanyModel.id == company_id))
        if company is None:
            raise ValueError(f"Company {company_id} was not found")
        if not company.is_active:
            raise ValueError(f"Company {company_id} is inactive")

        generated = generate_api_key()
        session.add(
            ApiKeyModel(
                id=uuid4(),
                company_id=company_id,
                name=name,
                key_prefix=generated.prefix,
                key_hash=generated.key_hash,
            )
        )
        await session.commit()
        return generated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an API key for an existing company")
    parser.add_argument("--company-id", required=True, type=UUID)
    parser.add_argument("--name", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        generated = asyncio.run(create_api_key(args.company_id, args.name))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print("API key created successfully.")
    print("Copy it now; it cannot be recovered later:")
    print(generated.raw_key)


if __name__ == "__main__":
    main()
