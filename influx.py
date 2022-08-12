from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import *
from DataPoint import *
from datetime import datetime
from time import time

def writeInfluxDBPoint(influxDbClient, bucket, dataPoint):

    timestamp = dataPoint.date

    with influxDbClient.write_api() as write_api:

        dict_structure = {
            "measurement": "nasdaq",
            "tags": {
                "symbol": dataPoint.symbol,
            },
            "fields": {
                "price": dataPoint.price,
            },
            "time": timestamp
        }
        print(f"dataPoint: {dict_structure}")
        point = Point.from_dict(dict_structure, WritePrecision.MS)
        write_api.write(bucket=bucket, record=point)
