"""add kitchen preparation time and restaurant operating hours

Revision ID: 0009_add_kitchen_and_operating_hours
Revises: 0008_add_audit_log_and_delivery_failed
Create Date: 2026-05-18 15:55:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_add_kitchen_and_operating_hours"
down_revision: Union[str, None] = "0008_add_audit_log_and_delivery_failed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add order fields
    order_columns = [col['name'] for col in inspector.get_columns('orders')]
    if 'preparation_time_minutes' not in order_columns:
        op.add_column("orders", sa.Column("preparation_time_minutes", sa.Integer(), nullable=True))
    if 'ready_for_pickup_at' not in order_columns:
        op.add_column("orders", sa.Column("ready_for_pickup_at", sa.DateTime(), nullable=True))
    if 'is_urgent' not in order_columns:
        op.add_column("orders", sa.Column("is_urgent", sa.Boolean(), nullable=False, server_default="0"))
    
    # Add restaurant fields
    restaurant_columns = [col['name'] for col in inspector.get_columns('restaurants')]
    if 'opening_time' not in restaurant_columns:
        op.add_column("restaurants", sa.Column("opening_time", sa.String(), nullable=True))
    if 'closing_time' not in restaurant_columns:
        op.add_column("restaurants", sa.Column("closing_time", sa.String(), nullable=True))
    if 'is_open' not in restaurant_columns:
        op.add_column("restaurants", sa.Column("is_open", sa.Boolean(), nullable=False, server_default="1"))
    if 'delivery_radius_km' not in restaurant_columns:
        op.add_column("restaurants", sa.Column("delivery_radius_km", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "is_urgent")
    op.drop_column("orders", "ready_for_pickup_at")
    op.drop_column("orders", "preparation_time_minutes")
    
    op.drop_column("restaurants", "delivery_radius_km")
    op.drop_column("restaurants", "is_open")
    op.drop_column("restaurants", "closing_time")
    op.drop_column("restaurants", "opening_time")
