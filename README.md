# vibe-sim-iot-weather

vibe programming exercise for iot weather collection simulation

# getting started
1. have python 3.11, duckdb and uv installed

2. clone repo

3. cd into repo

4. `uv venv` and `source .venv/bin/activate`

5. `uv sync`

6a. `python scripts/run_web_app.py` and go to 127.0.0.1:5000 for ui

6b. `python scripts/run_multi_device.py` to generate fake data from a number of devices to a persistent duckdb store called `iot_data.duckdb`


# thoughts
pretty wild to get a something up and running within a few hours. i can generate fake data and have a ui in front of duckdb to show data.