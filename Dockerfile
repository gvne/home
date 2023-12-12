# syntax=docker/dockerfile:1
FROM ubuntu:22.04 AS base
RUN apt update && \
  apt install -y \
    git \
    python3-pip \
    python3.11 \
    python3.11-dev \
    python3-psycopg2 \
    && \
  apt clean
RUN python3.11 -m pip install --upgrade pip
COPY requirements.txt .
RUN python3.11 -m pip install -r requirements.txt

FROM base AS alembic
RUN apt update && \
  apt install -y \
    libpq-dev \
    postgresql-client \
    && \
  apt clean

COPY ./alembic alembic
COPY ./alembic/alembic.ini .
ENTRYPOINT [ "bash", "alembic/entrypoint.sh" ]

FROM base AS thermostat
COPY thermostat/requirements.txt .
RUN python3.11 -m pip install -r requirements.txt
COPY thermostat thermostat

ENTRYPOINT [ "python3.11", "-m", "thermostat" ]

FROM base AS weather
COPY weather/requirements.txt .
RUN python3.11 -m pip install -r requirements.txt
COPY weather weather

ENTRYPOINT [ "python3.11", "-m", "weather" ]
