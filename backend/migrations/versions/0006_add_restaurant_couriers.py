"""add restaurant couriers link table

Revision ID: 0006_add_restaurant_couriers
Revises: 0005_add_blacklist_location_cancel
Create Date: 2026-05-18 15:08:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_add_restaurant_couriers"
down_revision: Union[str, None] = "0005_add_blacklist_location_cancel"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS restaurant_couriers")
    op.create_table(
        "restaurant_couriers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("courier_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("courier_id", name="uq_restaurant_couriers_courier_id"),
        sa.UniqueConstraint("restaurant_id", "courier_id", name="uq_restaurant_couriers_restaurant_courier"),
    )
    op.create_index("ix_restaurant_couriers_restaurant_id", "restaurant_couriers", ["restaurant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_restaurant_couriers_restaurant_id", table_name="restaurant_couriers")
    op.drop_table("restaurant_couriers")
