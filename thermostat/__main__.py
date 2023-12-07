import sys
import os
import argparse
import getpass
import pathlib
import json
import datetime
import time
import logging

import pydantic
import th1

import thermostat.database
from thermostat.model.record import Record


logging.getLogger().setLevel(logging.DEBUG)
CACHE_PATH = pathlib.Path("/cache")
QUERY_PERIOD = datetime.timedelta(minutes=2)
ERROR_SLEEP_DURATION = datetime.timedelta(seconds=10)


class Parameters(pydantic.BaseModel):
    thermostat_id: str | None = None
    smartphone_id: str | None = None

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


def loop(client: th1.Client, params: Parameters):
    previous_time: datetime.datetime | None = None
    while True:
        if previous_time is not None:
            time.sleep(QUERY_PERIOD.total_seconds())

        info = client.get_thermostat_info(params.thermostat_id, params.smartphone_id)
        if previous_time == info.date:
            continue
        record = Record(
            time = info.date,
            temperature_degc = info.temperature, 
            humidity_percent = info.humidity,
            battery_percent = info.battery,
            consigne_degc = info.temperature_consigne,
            mode = info.mode
        )

        # Deal with derogation
        if info.latest_derogation is not None:
            is_in_derogation = info.latest_derogation.finish_at > datetime.datetime.now(
                tz=datetime.timezone.utc
            ) and info.latest_derogation.started_at <= datetime.datetime.now(
                tz=datetime.timezone.utc
            )
            if is_in_derogation:
                record.consigne_degc = info.latest_derogation.temperature
                record.mode = info.latest_derogation.heating_mode
        
        try:
            db = thermostat.database.get()
            s = next(db)

            if s.query(Record).filter(Record.time == record.time).first() is not None:
                logging.info("Record already exists")
            else:
                s.add(record)
                s.commit()
                logging.info("Record properly addded")
            previous_time = info.date
        except Exception as e:
            logging.error(f"Failed to add record: {e}")
            time.sleep(ERROR_SLEEP_DURATION.total_seconds())


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="th1.client", description="Somfy th1 api client"
    )
    parser.add_argument("-l", "--login", action="store_true")
    parser.add_argument("-t", "--thermostat", help="the thermostat ID")
    parser.add_argument("-s", "--smartphone", help="the smartphone ID")
    parser.add_argument(
        "-c", "--clear", help="Clear parameter cache", action="store_true"
    )
    parser.add_argument("--dry", help="Do not start the loop", action="store_true")
    args = parser.parse_args()

    # deal with login
    client = th1.Client(cache_path=CACHE_PATH / ".th1_cache")
    if args.login:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        client.login(username, password)

    param_cache = CACHE_PATH / ".parameters"
    if args.clear:
        os.remove(str(param_cache))

    parameters = Parameters.from_cache(param_cache)

    if args.thermostat:
        parameters.thermostat_id = args.thermostat
        parameters.to_cache(param_cache)

    if parameters.thermostat_id is None:
        thermostsats = client.get_thermostats()
        print("Please select a thermostat:")
        for t in thermostsats.results:
            print(f"* {t.id}")
        return -1

    if args.smartphone:
        parameters.smartphone_id = args.smartphone
        parameters.to_cache(param_cache)

    if parameters.smartphone_id is None:
        smartphones = client.get_smartphones(parameters.thermostat_id)
        print("Please select a smartphones:")
        for s in smartphones:
            print(f"* {s.vendor_id} ({s.name})")
        return -1

    if args.dry:
        print("System configured")
        return 0

    # run !
    loop(client, parameters)


if __name__ == "__main__":
    sys.exit(main())
