# nasdaq-data

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
[![Linux](https://img.shields.io/badge/os-Linux-green)](https://img.shields.io/badge/os-Linux-green)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://img.shields.io/badge/Python-3.10%2B-blue)
[![InfluxDB 1.8](https://img.shields.io/badge/InfluxDB-1.8-orange)](https://img.shields.io/badge/InfluxDB-1.8-orange)
[![InfluxDB 2](https://img.shields.io/badge/InfluxDB-2-orange)](https://img.shields.io/badge/InfluxDB-2-orange)

## What is it?

A (more or less) simple script that reads data from the Nasdaq Data Link / Quandl API and stores it in an InfluxDB.

You need a free API key from https://data.nasdaq.com. They do have a few free services that you can access with this key. However, what I am currently experiencing is that (at least with the data that I am looking for, the data is not really up to date).

I have a Grafana dashboard that this displays the current fuel prices and I would like to set them in relation to the current oil price - and since I am living in Europe - multiply that with the US$/EUR exchange rate. Nasdaq provides daily (that means: once per day) oil and echange rate prices/values. 

However just because the website for a specific data set, e.g. https://data.nasdaq.com/data/BOE/XUDLERD-spot-exchange-rate-euro-into-us says "Refreshed" on the current day, doesn't mean the data is from the current day. In this example, I called this website on June 21, 2022 and the newest available data is from June 17, 2022. So that is rather disappointing.

The script uses the _nasdaqdatalink_ library for Python (installed via pip).

## Disclaimer

I am not a professional programmer (any more), thus this code will most probably not live up to current standards. 

Version 1.0 of this script has been hacked together more or less quick and dirty. I plan to add comments and clean up the code in the future, but up to now it is not well documented.

**I will take no responsibility whatsoever for any damage that may result by using this code.**

## Requirements

* Python 3.10 or higher (currently works under 3.7+)
* additional Python modules: see requirements.txt
* A free API key from https://data.nasdaq.com
* An InfluxDB to store the values.
  * Release 2.0+ of this script handles both InfluxDB 1.8 and 2.x (see _Configuration values_ below)
* (Grafana for visualization)

### Installation

1. Clone the git repository from https://github.com/LordOfTheSnow/nasdaq-data.git
2. Change to the created directory
3. Create a Python virtual environment with `python3 -m venv venv`
4. Activate that virtual environment with `source venv/bin/activate`
5. Install the required Python modules via pip: `pip install -r requirements.txt`
6. Create a file `.nasdaq/data_link_apikey` and put in the plain API key you obtained at https://data.nasdaq.com
7. Rename the provided file _.env.example_ to _.env_ and put in the configuration values

### Updating from V1
1. Delete your whole virtual environment you created in step 3 of the installation process
2. Create a new Python virtual environment with `python3 -m venv venv`
3. Activate that virtual environment with `source venv/bin/activate`
4. Install the required Python modules via pip: `pip install -r requirements.txt`
5. The configuration values for InfluxDB 1.8 have changed slightly, see _Configuration values_

Hint: If you see this error message (I got this on my Raspberry Pi (32 Bit) that still uses Python 3.7) when installing the needed python modules in step 5

> No matching distribution found for numpy==1.22.4 (from -r requirements.txt (line 4))

install pandas by hand (in your virtual environment):

```
pip install pandas
```

#### Configuration values (.env)

There are various methods in InfluxDB 2 to read configuration values. I decided to stick with the .env file file because it is also possible to set the config values for InfluxDB 2 via environment variables and they will still be read with by the dotenv-python package - so it's up to you if you set those values in the .env file or as enviroment variables.

The configuration values for accessing InfluxDB 1.8 must be set in the .env file, they are **not* read from the environment. **Note the slight changes for release V2 below!**

* loglevel = logging.INFO - set to one of the values listed under https://docs.python.org/3/library/logging.html#levels

* {**new in V2**} influxVersion = "2" - decides whether to use InfluxDB 1.8 (=="1") or InfluxDB 2 (=="2", default)

* only for InfluxDB V1.8
  * {**new in V2**} influxUrl = full URL including protocol and port to the InfluxDB server, e.g. `"http://localhost:8086"`
  * {**removed in V2**} ~~influxPort = 8086~~
  * influxDbName = "stockdata"
  * influxRetentionPolicy = "your retention policy" - if you use your own retention policy here, do provide it here, otherwise comment out the whole line (by adding a hashmark '#' at the beginning of the line)

* only for InfluxDB V2 (these values may be omitted in the .env file and set directly as environment variables)
  * INFLUXDB_V2_URL = "http://localhost:8086"
  * INFLUXDB_V2_ORG = "MyOrg"
  * INFLUXDB_V2_TOKEN = "My Token"
  * INFLUXDB_V2_BUCKET = "stockdata"

The InfluxDB server and the database or bucket ("stockdata" in this example) have to exist already. I used the following influx command to create the database in InfluxDB V1.8:

`create database stockdata with duration 365d replication 1 shard duration 7d name one_year`

Use shorter values for the _duration_ and _shard duration_ if you want to. (The _duration_ values will determine how long the data will be stored until it will be automatically removed.)

If you use InfluxDB 2, use the Influx GUI to set up your organzination, bucket and token.


### Usage 

#### Run from shell

8. From within the virtual environment, call the script with 

```
python app.py SYMBOL --start_date YYYY-MM-DD --end_date YYYY-MM-DD --do_not_write
python app.py SYMBOL --start_date -2 --end_date -1 --do_not_write
```

_SYMBOL_ has to be a Nasdaq Data Link ticker symbol. You can find the symbol in the upper right corner of the webpage that is displaying that symbol's data. 

Examples
* https://data.nasdaq.com/data/OPEC/ORB-opec-crude-oil-price - The symbol to use here is `OPEC/ORB`
* https://data.nasdaq.com/data/BOE/XUDLERD-spot-exchange-rate-euro-into-us - The symbol to use here is `BOE/XUDLERD`


Run 
```
python app.py -h
```
for a help page

Options starting with a _-_ or _--_ are optional and can be omitted.

If `--start_date` and/or `--end_date` are omitted, the current day will be taken. If a negative offset (e.g. `-1`) is given, the current date minus that number of days will be taken (e.g. -1 day)

If `--do_not_write` is given, no values are written to the database

#### Run via periodically via cron

If you want to run this script periodically via cron, you can call the wrapper script **cronscript.sh** (rename the provided `cronscript.sh.example` to `cronscript.sh` so that local changes will not be overwritten with next git pull).

8. Set execute permissions for the script: `chmod ug+x cronscript.sh`
9. Call `crontab -e` to edit the cron table (crontab), e.g.:

```
# m h  dom mon dow   command
30 14 * * * /home/pi/src/nasdaq-data/cronscript.sh
```
This will run the command at 14:30h local time on every day. Edit the path to the script to wherever you put it. 
The script assumes you have a Python virtual environment created with `python3 -m venv venv` in the same directory where you checked out the repository. The script will activate the virtual environment, call the Python interpreter with the script and will deactivate the virtual environment then.

### Files and data created

1. measurement _nasdaq_ in the Influx DB/bucket configured under _influxDbName_ / _INFLUXDB_V2_BUCKET_ 

```
{
    "measurement": "nasdaq",
    "tags": {
        "symbol": dataPoint.symbol,
    },
    "fields": {
        "price": dataPoint.price,
    },
    "time": timestamp
}
```

In the current implementation, the timestamp will always be at 0:00 local time at the given date. This is due to my current usecase that just uses Nasdaq data that are only delivered daily (or should be delivered daily).

## Known bugs & limitations

* Currently database authentiction in Influx DB 1.8 is not supported and most probably won't be implemented in the future as Influx DB 1.8 phases out

## Additional documentation used 

* https://data.nasdaq.com/tools/python

## History

* 03-Jan-2023
  * V2.0.1: updated requirements.txt due to security issue in certifi
  
* 14-Aug-2022
  * Released V2.0 which can also handle Influx DB 2.x 

* 24-Jun-2022
  * added possibilty to use offsets for the `start_date` and `end_date` parameters. You can now use `--start_date -2` to set the start date to the current date - 2 days.
  * added example file _cronscript.sh.example_ to run this script in a Python virtual environment via cron

* 21-Jun-2022
  * made repository public
