import os
import pandas
import numpy
import logging
import nasdaqdatalink
from dotenv import load_dotenv
from argparse import ArgumentParser
from datetime import datetime
from influx18 import *

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
    influxServer=os.environ.get('influxServer')
    influxPort=os.environ.get("influxPort", default=8086)
    influxDbName=os.environ.get("influxDbName", default="nasdaq")

    # parse command line arguments    
    parser = ArgumentParser()
    parser.add_argument("symbol", 
                        help="Ticker symbol (==Nasdaq Data Link Code), e.g. OPEC/ORB for OPEC Crude Oil)")
    parser.add_argument("-sd", "--start_date", 
                        help="start date for the values to be received. Format: 'YYYY-MM-DD'")
    parser.add_argument("-ed", "--end_date", 
                        help="end date for the values to be received. Format: 'YYYY-MM-DD'")
    parser.add_argument("-dnw", "--do_not_write", action='store_true',
                        help="do not write values to database")

    parser.add_argument                        
    args = parser.parse_args()
    data_link_log.debug(f"symbol: {args.symbol}")


    # create an influxDBClient
    influxDbClient = InfluxDBClient(host=influxServer, port=influxPort)
    influxDbClient.switch_database(influxDbName)


    # get start and end date
    # first get the current date
    utcnow = datetime.utcnow()
    start_date = utcnow.strftime("%Y-%m-%d")
    end_date = utcnow.strftime("%Y-%m-%d")
    data_link_log.debug(f"start_date (calculated): {start_date}")
    data_link_log.debug(f"end_date (calculated): {end_date}")

    if args.start_date:
        start_date = args.start_date
    data_link_log.debug(f"start_date (set): {start_date}")
    if args.end_date:
        end_date = args.end_date
    data_link_log.debug(f"end_date (set): {end_date}")

    # read the data
    data = nasdaqdatalink.Dataset(args.symbol).data(params={ 'start_date':start_date, 'end_date':end_date})
    if data:
        df = data.to_pandas()
        print(df.head())
        if not args.do_not_write:
            for index, row in df.iterrows():
                dataPoint = DataPoint(args.symbol,index, row['Value'])
                # data_link_log.debug(f"date: {index}")
                # data_link_log.debug(f"dataPoint: {dataPoint.date}, {dataPoint.price}")
                writeInfluxDBPoint(influxDbClient, dataPoint)  
        else:
            data_link_log.info("--do_not_write specified, no data written to database")  
    else:
        data_link_log.info(f"no data between {start_date} - {end_date}")



if __name__ == '__main__':
    main()
