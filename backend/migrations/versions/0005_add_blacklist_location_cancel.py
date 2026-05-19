"""add token blacklist, courier locations, order cancel_reason

Revision ID: 0005_add_blacklist_location_cancel
Revises: 0004_add_user_tokens
Create Date: 2026-05-18 14:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_add_blacklist_location_cancel"
down_revision: Union[str, None] = "0004_add_user_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_blacklist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(), nullable=False, unique=True),
        sa.Column("blacklisted_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_token_blacklist_token", "token_blacklist", ["token"], unique=True)

    op.create_table(
        "courier_locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("courier_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("bearing", sa.Float(), nullable=True),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_courier_locations_courier_id", "courier_locations", ["courier_id"], unique=True)

    op.add_column("orders", sa.Column("cancel_reason", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "cancel_reason")
    op.drop_index("ix_courier_locations_courier_id", table_name="courier_locations")
    op.drop_table("courier_locations")
    op.drop_index("ix_token_blacklist_token", table_name="token_blacklist")
    op.drop_table("token_blacklist")
