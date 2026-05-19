"""add audit log and delivery failed status

Revision ID: 0008_add_audit_log_and_delivery_failed
Revises: 0007_add_courier_status_tracking_fee
Create Date: 2026-05-18 15:48:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_add_audit_log_and_delivery_failed"
down_revision: Union[str, None] = "0007_add_courier_status_tracking_fee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "order_status_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False, index=True),
        sa.Column("old_status", sa.String(), nullable=True),
        sa.Column("new_status", sa.String(), nullable=False),
        sa.Column("changed_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_order_status_logs_created_at", "order_status_logs", ["created_at"])

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('orders')]
    
    if 'delivery_failed_at' not in columns:
        op.add_column("orders", sa.Column("delivery_failed_at", sa.DateTime(), nullable=True))
    if 'return_reason' not in columns:
        op.add_column("orders", sa.Column("return_reason", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_index("ix_order_status_logs_created_at", table_name="order_status_logs")
    op.drop_table("order_status_logs")
    
    op.drop_column("orders", "return_reason")
    op.drop_column("orders", "delivery_failed_at")
