"""Create thermostat tables

Revision ID: db6b020753af
Revises: 
Create Date: 2023-12-06 20:52:43.207128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "db6b020753af"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "thermostat_record",
        sa.Column("time", sa.TIMESTAMP(timezone=True), primary_key=True),
        sa.Column("temperature_degc", sa.Float),
        sa.Column("humidity_percent", sa.Float),
        sa.Column("consigne_degc", sa.Float),
        sa.Column("battery_percent", sa.Float),
        sa.Column("mode", sa.String)
    )
    op.execute("SELECT create_hypertable('thermostat_record', 'time')")


def downgrade() -> None:
    op.drop_table("thermostat_record")
