How to run:

Redis Cache:
cd .\data\ru-bus-gtfsrt\
docker compose up

Live GTFS Redis Ingestor:
cd .\data\ru-bus-gtfsrt\
python gtfs_rt_ingestor.py

Nightly Job:
python src\tasks\nightly_refresh.py

UI:
