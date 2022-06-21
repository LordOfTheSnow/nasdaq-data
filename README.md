# nasdaq.data

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
[![Linux](https://img.shields.io/badge/os-Linux-green)](https://img.shields.io/badge/os-Linux-green)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://img.shields.io/badge/Python-3.10%2B-blue)
[![InfluxDB 1.8](https://img.shields.io/badge/InfluxDB-1.8-orange)](https://img.shields.io/badge/InfluxDB-1.8-orange)

## What is it?

A (more or less) simple script that reads data from the Nasdaq Data Link / Quandl API and stores it in an InfluxDB.

You need a free API key from https://data.nasdaq.com. They do have a few free services that you can access with this key. However, what I am currently experiencing is that (at least with the data that I am looking for, the data is not really up to date).

I have Grafana dashboard that this displays the current fuel prices and I would like to set them in relation to the current oil price - and since I am living in Europe - multiply that with the US$/EUR exchange rate. Nasdaq provides daily (that means: once per day) oil and echange rate prices/values. 

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
