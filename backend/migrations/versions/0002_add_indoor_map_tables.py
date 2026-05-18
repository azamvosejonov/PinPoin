"""add indoor map tables

Revision ID: 0002_add_indoor_map_tables
Revises: 0001_create_tables
Create Date: 2026-05-18 12:10:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_add_indoor_map_tables"
down_revision: Union[str, None] = "0001_create_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "indoor_maps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("building_id", sa.Integer(), sa.ForeignKey("buildings.id"), nullable=False, unique=True),
        sa.Column("anchor_latitude", sa.Float(), nullable=True),
        sa.Column("anchor_longitude", sa.Float(), nullable=True),
        sa.Column("anchor_altitude", sa.Float(), nullable=True),
        sa.Column("floors", sa.JSON(), nullable=False),
        sa.Column("extras", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_indoor_maps_building_id", "indoor_maps", ["building_id"], unique=True)

    op.create_table(
        "indoor_paths",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("indoor_map_id", sa.Integer(), sa.ForeignKey("indoor_maps.id"), nullable=False),
        sa.Column("courier_id", sa.String(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("path", sa.JSON(), nullable=False),
    )
    op.create_index("ix_indoor_paths_indoor_map_id", "indoor_paths", ["indoor_map_id"])
    op.create_index("ix_indoor_paths_courier_id", "indoor_paths", ["courier_id"])
    op.create_index("ix_indoor_paths_recorded_at", "indoor_paths", ["recorded_at"])


def downgrade() -> None:
    op.drop_index("ix_indoor_paths_recorded_at", table_name="indoor_paths")
    op.drop_index("ix_indoor_paths_courier_id", table_name="indoor_paths")
    op.drop_index("ix_indoor_paths_indoor_map_id", table_name="indoor_paths")
    op.drop_table("indoor_paths")

    op.drop_index("ix_indoor_maps_building_id", table_name="indoor_maps")
    op.drop_table("indoor_maps")
