"""Create weather tables

Revision ID: 095594208503
Revises: db6b020753af
Create Date: 2023-12-12 21:26:20.751352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "095594208503"
down_revision: Union[str, None] = "db6b020753af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "current_weather",
        sa.Column("time", sa.TIMESTAMP(timezone=True), primary_key=True),
        sa.Column("temperature_degc", sa.Float),
        sa.Column("humidity_percent", sa.Float),
    )
    op.execute("SELECT create_hypertable('current_weather', 'time')")


def downgrade() -> None:
    op.drop_table("current_weather")
