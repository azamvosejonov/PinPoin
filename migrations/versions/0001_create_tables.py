from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = "0001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "buildings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("external_id", sa.String, unique=True, nullable=False),
        sa.Column("address", sa.String, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("building_type", sa.String, nullable=False, server_default="OTHER"),
        sa.Column("difficulty_index", sa.Integer, nullable=False, server_default="1"),
        sa.Column("has_lift", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("requires_chip", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("entrance_hint", sa.String, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_buildings_external_id", "buildings", ["external_id"], unique=True)

    op.create_table(
        "entrances",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("building_id", sa.Integer, sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("domofon_code", sa.String, nullable=True),
        sa.Column("has_barrier", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("validated_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_validated_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_entrances_building_id", "entrances", ["building_id"])

    op.create_table(
        "trajectories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("building_id", sa.Integer, sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("courier_id", sa.String, nullable=False),
        sa.Column("delivered_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("points", sqlite.JSON, nullable=False),
    )
    op.create_index("ix_trajectories_building_id", "trajectories", ["building_id"])

    op.create_table(
        "delivery_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.String, nullable=False, unique=True),
        sa.Column("courier_id", sa.String, nullable=False),
        sa.Column("building_id", sa.Integer, sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_time", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("end_time", sa.DateTime, nullable=True),
        sa.Column("temperature_model", sa.String, nullable=False),
        sa.Column("start_temperature", sa.Float, nullable=False),
        sa.Column("predicted_temperature", sa.Float, nullable=False),
        sa.Column("predicted_eta_minutes", sa.Integer, nullable=False),
        sa.Column("transport_mode", sa.String, nullable=True),
    )
    op.create_index("ix_sessions_courier_id", "delivery_sessions", ["courier_id"])


def downgrade() -> None:
    op.drop_index("ix_sessions_courier_id", table_name="delivery_sessions")
    op.drop_table("delivery_sessions")
    op.drop_index("ix_trajectories_building_id", table_name="trajectories")
    op.drop_table("trajectories")
    op.drop_index("ix_entrances_building_id", table_name="entrances")
    op.drop_table("entrances")
    op.drop_index("ix_buildings_external_id", table_name="buildings")
    op.drop_table("buildings")
