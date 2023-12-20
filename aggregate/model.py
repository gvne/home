import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

import aggregate.database


class HeatingStatistic(aggregate.database.BaseModel):
    __tablename__ = "heating_statistic"

    time: so.Mapped[datetime.datetime] = so.mapped_column(primary_key=True)
    heating_duration_over_last_hour_m: so.Mapped[float]
