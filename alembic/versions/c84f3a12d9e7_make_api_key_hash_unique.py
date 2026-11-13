"""Make API key hashes unique.

Revision ID: c84f3a12d9e7
Revises: a58dadfebd86
Create Date: 2026-11-12
"""

from collections.abc import Sequence

from alembic import op

revision: str = "c84f3a12d9e7"
down_revision: str | None = "a58dadfebd86"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint("uq_api_keys_key_hash", "api_keys", ["key_hash"])


def downgrade() -> None:
    op.drop_constraint("uq_api_keys_key_hash", "api_keys", type_="unique")
