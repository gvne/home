"""Create aggregates

Revision ID: 103bd308f095
Revises: 095594208503
Create Date: 2023-12-19 20:51:32.843613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '103bd308f095'
down_revision: Union[str, None] = '095594208503'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "heating_statistic",
        sa.Column("time", sa.TIMESTAMP(timezone=True), primary_key=True),
        sa.Column("heating_duration_over_last_hour_m", sa.Float)
    )
    op.execute("SELECT create_hypertable('heating_statistic', 'time')")


def downgrade() -> None:
    op.drop_table("heating_statistic")
