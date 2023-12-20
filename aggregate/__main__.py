import sys
import time
import datetime
import logging

from sqlalchemy.sql import text

import aggregate.database
import aggregate.model

QUERY_PERIOD = datetime.timedelta(minutes=5)

QUERY = text("""
SELECT count(minute) FROM (
  SELECT
    time_bucket_gapfill(
        '1 minute', "time",
        start => NOW() - interval '1439 minutes', 
        finish => NOW()) AS minute,
    interpolate(avg(temperature_degc)) AS temperature,
    locf(avg(consigne_degc)) AS consigne
  FROM thermostat_record
  WHERE time >= NOW() - interval '1439 minutes'
  GROUP BY minute
  ORDER BY minute
) AS SubQuery
WHERE temperature <= consigne
""")

def main():
    logging.getLogger().setLevel(logging.DEBUG)

    while True:
        db = aggregate.database.get()    
        s = next(db)
        resp = s.execute(QUERY)
        duration = datetime.timedelta(minutes=int(resp.first()[0]))
        logging.info(f"Heating duration over the last 1h: {duration}")
        
        s.add(
            aggregate.model.HeatingStatistic(
                time=datetime.datetime.now(),
                heating_duration_over_last_hour_m=duration.total_seconds() / 60
            )
        )
        s.commit()
        s.close()
        time.sleep(QUERY_PERIOD.total_seconds())


if __name__ == "__main__":
    sys.exit(main())
