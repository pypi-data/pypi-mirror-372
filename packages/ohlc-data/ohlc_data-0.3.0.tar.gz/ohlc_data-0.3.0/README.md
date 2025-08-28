# OHLC-DATA

Easily download OHLC data from either alpaca (requires API keys) or yfinance to csv files<br>
To acquire API keys for alpaca visit:
https://alpaca.markets/

## Instructions
- Open your preferred CLI (Terminal/Command Prompt etc)
- Create and activate a Python virtual environment

**Mac/Linux**<br>
	
	python3 -m venv <venv>
	source ./<venv>/bin/activate
	
**Windows**<br>
	
	python -m venv <venv>
	./<venv>/Scripts/activate

## Installation
**Mac/Linux**<br>

	pip3 install ohlc-data
	
**Windows**<br>

	pip install ohlc-data
	
## Download OHLC data
	ohlc_download

Running this script will create a folder in the current directory called 'ohlc_csv' if there isn't one already by that name. It will then take you through a series of prompts:<br>

<img src='./example_pics/ohlc_download_script.png'/>

### Download data for one or multiple symbols
You can choose to get data for one symbol or multiple symbols at once. Symbols are not case sensitve.

<img src='./example_pics/multi_symbols.png'/>

### Choose source
You can then choose which API to use. Alpaca requires API keys that you'll be prompted to enter, yfinance does not require API keys.<br>

### Valid Periods and Intervals (Timeframes)
Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max<br>
Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo<br> 

**yfinance:**<br>
	
- 1m data cannot extend past 7 days
- 2m - 30m data, and 90m data cannot extend past 60 days
- 1h data cannot extend past 730 days
- 1d - 3mo data allows max available data
	
**alpaca:**<br>
	
- Data from 2016 to present is available for all intervals

### Start and End Dates (Optional)
To get data from a specifc date range, leave **Period** blank and instead use the **Start date** and **End date** fields.<br>

<img src='./example_pics/choose_source.png'/>







