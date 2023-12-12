# My home automation

This repository tracks my personal home automation (more home monitoring for now). 

## Setup overview

TODO

## Thermostat

Initialize the configuration
```bash
docker compose build
docker compose run -it --rm thermostat --dry -l
# login
docker compose run -it --rm thermostat --dry
# select the right thermostat and smartphone (-t / -s)
```
