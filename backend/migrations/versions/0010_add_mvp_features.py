"""add MVP critical features (total_amount, payment_method, logo_url)

Revision ID: 0010_add_mvp_features
Revises: 0009_add_kitchen_and_operating_hours
Create Date: 2026-05-18 16:10:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010_add_mvp_features"
down_revision: Union[str, None] = "0009_add_kitchen_and_operating_hours"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add order fields
    order_columns = [col['name'] for col in inspector.get_columns('orders')]
    if 'total_amount' not in order_columns:
        op.add_column("orders", sa.Column("total_amount", sa.Float(), nullable=True))
    if 'payment_method' not in order_columns:
        op.add_column("orders", sa.Column("payment_method", sa.String(), nullable=True))
    
    # Add restaurant field
    restaurant_columns = [col['name'] for col in inspector.get_columns('restaurants')]
    if 'logo_url' not in restaurant_columns:
        op.add_column("restaurants", sa.Column("logo_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "payment_method")
    op.drop_column("orders", "total_amount")
    op.drop_column("restaurants", "logo_url")
