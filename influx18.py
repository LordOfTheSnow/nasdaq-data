from influxdb import InfluxDBClient
from DataPoint import *
from datetime import datetime
from time import time

def writeInfluxDBPoint(influxDbClient, dataPoint):

    # timestamp = int(dataPoint.date.timestamp())
    timestamp = dataPoint.date

    json_body = [
        {
            "measurement": "nasdaq",
            "tags": {
                "symbol": dataPoint.symbol,
            },
            "fields": {
                "price": dataPoint.price,
            },
            "time": timestamp
            # "time": datetime.utcnow()
        }
    ]
    print(f"json_body: {json_body}")
    influxDbClient.write_points(json_body, time_precision="ms")
