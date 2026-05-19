"""add user tokens table

Revision ID: 0004_add_user_tokens
Revises: 0003_add_auth_and_orders
Create Date: 2026-05-18 13:55:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0004_add_user_tokens"
down_revision: Union[str, None] = "0003_add_auth_and_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(), nullable=False, unique=True),
        sa.Column("purpose", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_user_tokens_token", "user_tokens", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_user_tokens_token", table_name="user_tokens")
    op.drop_table("user_tokens")
