"""fix critical issues part 2 (cash balance, race condition, unassignable, offline validation, return status)

Revision ID: 0012_fix_critical_issues_part2
Revises: 0011_fix_critical_issues
Create Date: 2026-05-18 16:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012_fix_critical_issues_part2"
down_revision: Union[str, None] = "0011_fix_critical_issues"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add courier_status field
    courier_status_columns = [col['name'] for col in inspector.get_columns('courier_status')]
    if 'cash_balance' not in courier_status_columns:
        op.add_column("courier_status", sa.Column("cash_balance", sa.Float(), default=0.0))
    
    # Add order fields
    order_columns = [col['name'] for col in inspector.get_columns('orders')]
    if 'max_retries' not in order_columns:
        op.add_column("orders", sa.Column("max_retries", sa.Integer(), default=3))
    if 'retry_count' not in order_columns:
        op.add_column("orders", sa.Column("retry_count", sa.Integer(), default=0))


def downgrade() -> None:
    op.drop_column("orders", "retry_count")
    op.drop_column("orders", "max_retries")
    op.drop_column("courier_status", "cash_balance")
