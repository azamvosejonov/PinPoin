"""add courier status, tracking hash, delivery fee

Revision ID: 0007_add_courier_status_tracking_fee
Revises: 0006_add_restaurant_couriers
Create Date: 2026-05-18 15:35:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_add_courier_status_tracking_fee"
down_revision: Union[str, None] = "0006_add_restaurant_couriers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS courier_status")
    
    op.create_table(
        "courier_status",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("courier_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("status", sa.String(), nullable=False, server_default="offline"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_online_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_courier_status_courier_id", "courier_status", ["courier_id"], unique=True)

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('orders')]
    
    if 'tracking_hash' not in columns:
        op.add_column("orders", sa.Column("tracking_hash", sa.String(), nullable=True))
    if 'delivery_distance_km' not in columns:
        op.add_column("orders", sa.Column("delivery_distance_km", sa.Float(), nullable=True))
    if 'delivery_fee' not in columns:
        op.add_column("orders", sa.Column("delivery_fee", sa.Float(), nullable=True))
    
    if 'tracking_hash' in columns:
        op.execute(
            "UPDATE orders SET tracking_hash = substr(hex(randomblob(16)), 1, 24) WHERE tracking_hash IS NULL"
        )
    
    if 'tracking_hash' in columns:
        try:
            op.create_index("ix_orders_tracking_hash", "orders", ["tracking_hash"], unique=True)
        except Exception:
            pass


def downgrade() -> None:
    op.drop_index("ix_orders_tracking_hash", table_name="orders")
    op.drop_column("orders", "delivery_fee")
    op.drop_column("orders", "delivery_distance_km")
    op.drop_column("orders", "tracking_hash")

    op.drop_index("ix_courier_status_courier_id", table_name="courier_status")
    op.drop_table("courier_status")
