"""fix critical issues (courier status, TTL, declined couriers, compensation)

Revision ID: 0011_fix_critical_issues
Revises: 0010_add_mvp_features
Create Date: 2026-05-18 16:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0011_fix_critical_issues"
down_revision: Union[str, None] = "0010_add_mvp_features"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add order fields for declined couriers and compensation
    order_columns = [col['name'] for col in inspector.get_columns('orders')]
    if 'declined_courier_ids' not in order_columns:
        op.add_column("orders", sa.Column("declined_courier_ids", sa.String(), nullable=True))
    if 'compensation_paid' not in order_columns:
        op.add_column("orders", sa.Column("compensation_paid", sa.Boolean(), default=False))


def downgrade() -> None:
    op.drop_column("orders", "compensation_paid")
    op.drop_column("orders", "declined_courier_ids")
