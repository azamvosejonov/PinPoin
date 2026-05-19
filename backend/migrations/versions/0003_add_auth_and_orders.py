"""add auth and orders tables

Revision ID: 0003_add_auth_and_orders
Revises: 0002_add_indoor_map_tables
Create Date: 2026-05-18 13:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003_add_auth_and_orders"
down_revision: Union[str, None] = "0002_add_indoor_map_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, default="courier"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("contact_phone", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("building_id", sa.Integer(), sa.ForeignKey("buildings.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_code", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("customer_name", sa.String(), nullable=True),
        sa.Column("customer_phone", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("items", sa.JSON(), nullable=True),
        sa.Column("dropoff_address", sa.String(), nullable=False),
        sa.Column("dropoff_latitude", sa.Float(), nullable=False),
        sa.Column("dropoff_longitude", sa.Float(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id"), nullable=False),
        sa.Column("building_id", sa.Integer(), sa.ForeignKey("buildings.id"), nullable=True),
        sa.Column("courier_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("picked_up_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("canceled_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("order_code", name="uq_orders_order_code"),
    )

    op.create_index("ix_orders_status", "orders", ["status"])


def downgrade() -> None:
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")
    op.drop_table("restaurants")
    op.drop_table("users")
