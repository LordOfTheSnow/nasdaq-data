import sys
import os
import pandas
import numpy
import logging
import nasdaqdatalink
from dotenv import load_dotenv
from argparse import ArgumentParser
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from DataPoint import *
from influx import *

def main():

    logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)  # optionally set level for everything.  Useful to see dependency debug info as well.

    data_link_log = logging.getLogger("nasdaqdatalink")
    data_link_log.setLevel(logging.DEBUG)
    # data_link_log.debug("Test")

    # set API key from a local directory and not from the user's home directory
    nasdaqdatalink.read_key(filename=".nasdaq/data_link_apikey")

    # load environment variables
    load_dotenv()

    # read InfluxDB config values from file ".env"
    influxVersion=os.environ.get("influxVersion", default="2")

    if influxVersion == "1":
        # InfluxDB V1.8
        influxUrl = os.environ.get('influxUrl')
        influxDbName = os.environ.get("influxDbName", default="nasdaq")
        influxRetentionPolicy = os.environ.get("influxRetentionPolicy")
        influxOrg = "-"

    elif influxVersion == "2":
        # InfluxDB V2+
        influxUrl = os.environ.get('INFLUXDB_V2_URL')
        influxOrg = os.environ.get('INFLUXDB_V2_ORG', default='-')
        influxToken= os.environ.get('INFLUXDB_V2_TOKEN')
        influxBucket= os.environ.get('INFLUXDB_V2_BUCKET')

    else:
        logging.exception('No InfluxDB version specified in configuration. Set influxVersion = "1" or "2" in .env. Program terminated.')
        sys.exit("InfluxDB configuration parameters are missing. Program terminated. See log file for details.")

    # parse command line arguments    
    parser = ArgumentParser()
    parser.add_argument("symbol", 
                        help="Ticker symbol (==Nasdaq Data Link Code), e.g. OPEC/ORB for OPEC Crude Oil)")
    parser.add_argument("-sd", "--start_date", 
                        help="start date for the values to be received. Format: 'YYYY-MM-DD' or a negative offset (e.g. -1 = -1 day)")
    parser.add_argument("-ed", "--end_date", 
                        help="end date for the values to be received. Format: 'YYYY-MM-DD' or a negative offset (e.g. -1 = -1 day)")
    parser.add_argument("-dnw", "--do_not_write", action='store_true',
                        help="do not write values to database")

    parser.add_argument                        
    args = parser.parse_args()
    data_link_log.debug(f"symbol: {args.symbol}")

    # get start and end date
    # first get the current date
    utcnow = datetime.utcnow()

    if args.start_date:
        if str(args.start_date).startswith("-"):
            start_date_ts = utcnow + timedelta(days=int(args.start_date))
            start_date = start_date_ts.strftime("%Y-%m-%d")
        else:
            start_date = args.start_date
    else:
        start_date = utcnow.strftime("%Y-%m-%d")
    data_link_log.debug(f"start_date: {start_date}")

    if args.end_date:
        if str(args.end_date).startswith("-"):
            end_date_ts = utcnow + timedelta(days=int(args.end_date))
            end_date = end_date_ts.strftime("%Y-%m-%d")
        else:
            end_date = args.end_date
    else:
        end_date = utcnow.strftime("%Y-%m-%d")
    data_link_log.debug(f"end_date: {end_date}")

    # read the data
    data = nasdaqdatalink.Dataset(args.symbol).data(params={ 'start_date':start_date, 'end_date':end_date})


    if influxVersion == "1":
        if (not (influxUrl and influxDbName)):
            logging.exception("InfluxDB configuration parameters are missing. Program terminated.")
            sys.exit("InfluxDB configuration parameters are missing. Program terminated. See log file for details.")

        # V1.8+ of InfluxDB does not use buckets, but the V2 api needs the bucket parameter
        #   that is created by the db name + the retention policy name in the format
        #   "db/rp"
        bucket = influxDbName 
        if influxRetentionPolicy:
            bucket += "/" + influxRetentionPolicy

        with InfluxDBClient(url=influxUrl, org='-') as influxDbClient:
            handleData(log=data_link_log, data=data, args=args, influxDbClient=influxDbClient, influxBucket=influxBucket, start_date=start_date, end_date=end_date)

    elif influxVersion == "2":
        if (not (influxUrl and influxToken and influxBucket)):
            logging.exception("InfluxDB configuration parameters are missing. Program terminated.")
            sys.exit("InfluxDB configuration parameters are missing. Program terminated. See log file for details.")

        with InfluxDBClient(url=influxUrl, token=influxToken, org=influxOrg) as influxDbClient:
            handleData(log=data_link_log, data=data, args=args, influxDbClient=influxDbClient, influxBucket=influxBucket, start_date=start_date, end_date=end_date)


# helper function because it is repeated for either InfluxDB 1.8 and 2
def handleData(log, data, args, influxDbClient, influxBucket, start_date, end_date):
    if data:
        df = data.to_pandas()
        # print(df.head())
        if not args.do_not_write:
            for index, row in df.iterrows():
                dataPoint = DataPoint(args.symbol,index, row['Value'])
                # log.debug(f"date: {index}")
                # log.debug(f"dataPoint: {dataPoint.date}, {dataPoint.price}")
                writeInfluxDBPoint(influxDbClient, influxBucket, dataPoint)  
        else:
            log.info("--do_not_write specified, no data written to database")  
    else:
        log.info(f"no data between {start_date} - {end_date}")


if __name__ == '__main__':
    main()
