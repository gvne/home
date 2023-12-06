import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

import thermostat.database


class Record(thermostat.database.BaseModel):
    __tablename__ = "thermostat_record"

    time: so.Mapped[datetime.datetime] = so.mapped_column(primary_key=True)
    temperature_degc: so.Mapped[float]
    humidity_percent: so.Mapped[float]
    consigne_degc: so.Mapped[float]
    battery_percent: so.Mapped[float]
    mode: so.Mapped[str]
