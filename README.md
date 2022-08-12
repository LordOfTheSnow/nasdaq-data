# nasdaq-data

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
[![Linux](https://img.shields.io/badge/os-Linux-green)](https://img.shields.io/badge/os-Linux-green)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://img.shields.io/badge/Python-3.10%2B-blue)
[![InfluxDB 1.8](https://img.shields.io/badge/InfluxDB-1.8-orange)](https://img.shields.io/badge/InfluxDB-1.8-orange)

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
  * I am currently still using InfluxDB 1.8 but plan to upgrade my home automation system soon and then I will provide a version for InfluxDB 2 as well
* (Grafana for visualization)

### Installation

1. Clone the git repository from https://github.com/LordOfTheSnow/nasdaq-data.git
2. Change to the created directory
3. Create a Python virtual environment with `python3 -m venv venv`
4. Activate that virtual environment with `source venv/bin/activate`
5. Install the required Python modules via pip: `pip install -r requirements.txt`
6. Create a file `.nasdaq/data_link_apikey` and put in the plain API key you obtained at https://data.nasdaq.com
7. Create a file _.env_ and put in the configuration values

Hint: If you see this error message (I got this on my Raspberry Pi (32 Bit) that still uses Python 3.7) when installing the needed python modules in step 5

> No matching distribution found for numpy==1.22.4 (from -r requirements.txt (line 4))

install pandas by hand (in your virtual environment):

```
pip install pandas
```

#### Configuration values (.env)

```
influxServer = "hostname of Influx DB Server" # hostname only, no schema, no trailing slash!, e.g. "raspberrypi" or "192.168.178.4"
influxPort = 8086
influxDbName = "nasdaq"
```

The InfluxDB server and the database _nasdaq_ have to exist already. I used the following influx command to create the InfluxDB:

`create database nasdaq with duration 365d replication 1 shard duration 7d name one_year`

Use shorter values for the _duration_ and _shard duration_ if you want to. (The _duration_ values will determine how long the data will be stored until it will be automatically removed.)


### Usage 

#### Run from shell

8. From within the virtual environment, call the script with 

```
python readdata.py SYMBOL --start_date YYYY-MM-DD --end_date YYYY-MM-DD --do_not_write
python readdata.py SYMBOL --start_date -2 --end_date -1 --do_not_write
```

_SYMBOL_ has to be a Nasdaq Data Link ticker symbol. You can find the symbol in the upper right corner of the webpage that is displaying that symbol's data. 

Examples
* https://data.nasdaq.com/data/OPEC/ORB-opec-crude-oil-price - The symbol to use here is `OPEC/ORB`
* https://data.nasdaq.com/data/BOE/XUDLERD-spot-exchange-rate-euro-into-us - The symbol to use here is `BOE/XUDLERD`


Run 
```
python readdata.py -h
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
This will run the command at 14:34h local time on every day. Edit the path to the script to wherever you put it. 
The script assumes you have a Python virtual environment created with `python3 -m venv venv` in the same directory where you checked out the repository. The script will activate the virtual environment, call the Python interpreter with the script and will deactivate the virtual environment then.

### Files and data created

1. measurement _nasdaq_ in the Influx DB configured under _influxDbName_

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

* Currently database authentiction is not yet supported but most probably will be in the future

## Additional documentation used 

* https://data.nasdaq.com/tools/python

## History

* 24-Jun-2021
  * added possibilty to use offsets for the `start_date` and `end_date` parameters. You can now use `--start_date -2` to set the start date to the current date - 2 days.
  * added example file _cronscript.sh.example_ to run this script in a Python virtual environment via cron

* 21-Jun-2021
  * made repository public
