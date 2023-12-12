import sys
import os
import time
import json
import pathlib
import argparse
import logging
import datetime

import requests
import pydantic

import weather.open_weather.constant as c
import weather.open_weather.schema as schema
import weather.open_weather.model as m
import weather.database

logging.getLogger().setLevel(logging.DEBUG)
CACHE_PATH = pathlib.Path("/cache")
POLLING_PERIOD = datetime.timedelta(minutes=2)
ERROR_SLEEP_DURATION = datetime.timedelta(seconds=10)


class Parameters(pydantic.BaseModel):
    coordinates: schema.Coordinates | None = None
    api_key: str | None = None

    @staticmethod
    def from_cache(path: pathlib.Path) -> "Parameters":
        if not path.exists():
            return Parameters()
        with open(path, "r") as f:
            data = f.read()
            data_json = json.loads(data)
            return Parameters.model_validate(data_json)

    def to_cache(self, path: pathlib.Path):
        with open(path, "w") as f:
            f.write(self.model_dump_json())


def loop(params: Parameters):
    assert params.api_key is not None
    assert params.coordinates is not None
    assert params.coordinates.lat is not None
    assert params.coordinates.lon is not None

    req = schema.CurrentRequest(
        lat=params.coordinates.lat, lon=params.coordinates.lon, appid=params.api_key
    )

    while True:
        try:
            raw_resp = requests.get(
                f"{c.API_ENDPOINT}/{c.WEATHER_ENDPOINT}", params=req.model_dump()
            )
            raw_resp.raise_for_status()
            resp = schema.CurrentResponse.model_validate_json(raw_resp.text)
        except Exception as e:
            logging.error(f"Failed to query weather: {e}")
            time.sleep(60)
            continue

        record = m.Record(
            time=resp.dt,
            temperature_degc=resp.main.temp,
            humidity_percent=resp.main.humidity,
        )

        # Add record to db
        db = weather.database.get()
        s = next(db)
        try:
            if (
                s.query(m.Record).filter(m.Record.time == record.time).first()
                is not None
            ):
                logging.info("Record already exists")
            else:
                s.add(record)
                s.commit()
                logging.info("Record properly addded")
                s.close()
            time.sleep(POLLING_PERIOD.total_seconds())
        except Exception as e:
            logging.error(f"Failed to add record: {e}")
            time.sleep(ERROR_SLEEP_DURATION.total_seconds())


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="Weather application", description="Store current weather in databse"
    )
    parser.add_argument("--latitude", help="store the latitude in cache")
    parser.add_argument("--longitude", help="store the longitude in cache")
    parser.add_argument("-k", "--key", help="store the api key in cache")
    parser.add_argument(
        "-c", "--clear", help="Clear parameter cache", action="store_true"
    )
    parser.add_argument("--dry", help="Do not start the loop", action="store_true")

    args = parser.parse_args()

    param_cache = CACHE_PATH / ".weather_parameters"
    if args.clear:
        os.remove(str(param_cache))

    parameters = Parameters.from_cache(param_cache)
    if args.latitude and args.longitude:
        parameters.coordinates = schema.Coordinates(
            lat=args.latitude, lon=args.longitude
        )
        parameters.to_cache(param_cache)

    if args.key:
        parameters.api_key = args.key
        parameters.to_cache(param_cache)

    if parameters.coordinates is None:
        print("Coordinates need to be consigured at least once")
        return -1
    if parameters.api_key is None:
        print("Key needs to be consigured at least once")
        return -1

    if args.dry:
        print("System configured")
        return 0

    loop(parameters)

    return 0


if __name__ == "__main__":
    sys.exit(main())
