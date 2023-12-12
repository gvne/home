import datetime
import sqlalchemy.orm as so

import weather.database


class Record(weather.database.BaseModel):
    __tablename__ = "current_weather"

    time: so.Mapped[datetime.datetime] = so.mapped_column(primary_key=True)
    temperature_degc: so.Mapped[float]
    humidity_percent: so.Mapped[float]
