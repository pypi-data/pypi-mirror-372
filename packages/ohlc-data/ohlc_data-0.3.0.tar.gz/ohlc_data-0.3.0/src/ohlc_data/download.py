import os
import datetime
import importlib

import ohlc_data
from ohlc_data.get import OHLC
from ohlc_data.authenticate import authenticate_alpaca
from ohlc_data.utils import validate_date


def main():
    """
    Creates ohlc_csv folder and timeframe subfolders, walks user through prompts to download
    OHLC data from Alpaca or Yahoo Finance APIs to appropriate folders
    """

    df = None 
    symbols = []

    # Acceptable period and interval
    period_accept = ['y','d']
    interval_accept = ['m','h','d']    

    # Valid Datetime formats
    start_date = None
    end_date = None
    date_format = '%Y-%m-%d'
    datetime_format = '%Y-%m-%d %H:%M:%S'

    # .env path for alpaca keys
    env_path = os.path.dirname(ohlc_data.__file__)
    ohlc_data_files = [f for f in os.listdir(env_path)]

    # Check for ohlc_csv folder
    print('\n','Checking for ohlc_csv folder...','\n')
    if not os.path.isdir('./ohlc_csv'):
        print('\n',f'ohlc_csv folder not found, creating ohlc_csv folder at {os.getcwd()}','\n')

        timeframes = ['m5','m15','m30','h1','h4','d1']
        os.mkdir('./ohlc_csv')
        for t in timeframes:
            os.mkdir(f'./ohlc_csv/{t}')
        
        print('\n','ohlc_csv folder created','\n')
    else:
        print('ohlc_csv found')

    # Choose Single Ticker or Multi-Ticker
    while True:
        print('\n')
        single_multi = input('Download data for one symbol (1) or multiple symbols? (2): ')
        if single_multi in ['1', '2']:
            single_multi = int(single_multi)
            break
        else:
            print('Invalid choice. Choose 1 or 2.')

    # Single Ticker chosen
    if single_multi == 1:
        while True:
            print('\n')
            symbol = input('Enter symbol: ').strip().upper()
            if len(symbol) <= 5:
                break
            else:
                print('You may have entered an invalid or unsupported symbol, try again')

    # Multi-Ticker chosen
    elif single_multi == 2:
        while True:
            print('\n')
            symbol_list = input('Enter symbols (separate symbols with single space, not case-sensitive): ').strip().upper()

            if not symbol_list:
                print('\n')
                print('You must enter at least one symbol.')
                continue
            
            symbol_split = symbol_list.split(' ')
            symbols = [symbol.strip() for symbol in symbol_split if symbol.strip()]

            length_check = [len(symbol.strip()) <= 5 for symbol in symbols]
            if False in length_check:
                print('\n')
                print('At least one symbol might have been input incorrectly, make sure to separate each symbol with a space')
                continue
            else:
                break

    # Choose source
    while True:
        print('\n')
        source = input('Source (1 for alpaca, 2 for yfinance): ')

        if source in ['1','2']:
            source = int(source)
        else:
            print('Invalid choice. Please choose 1 or 2.')
            continue

        if source == 1 and '.env' not in ohlc_data_files:
            authenticate_alpaca(env_path)
            importlib.reload(ohlc_data.get)
            break
        else:
            break
    
    # Choose period
    while True:
        print('\n')
        period = input('Period: ')

        if period:
            if period[-1] in period_accept and len(period) <= 4:
                break
            else:
                print('\n')
                print('Invalid input','\n','Valid periods: [number]y or [number]d')
                continue
        else:
            break

    # Choose interval
    while True: 
        print('\n')
        interval = input('Interval: ')
        
        if not interval:
            print('\n')
            print('Interval required')
            continue
        else:
            if  interval[-1] in interval_accept and len(interval) <= 3:
                break
            else:
                print('\n')
                print('Invalid input','\n', 'Valid intervals: [number]m, [number]h, [number]d ')
                continue

    # End date/datetime optional if period    
    if period:
        if 'd' in interval:
            while True:
                print('\n')
                end_input = input('End date (YYYY-MM-DD) (Optional) : ')
                if end_input and not validate_date(end_input, date_format):
                    print('Invalid date, ensure YYYY-MM-DD format')
                    continue
                else:
                    end_date = end_input
                    break
        else:
            while True:
                print('\n')
                end_input = input('End Datetime (YYYY-MM-DD HH:MM:SS) (Optional) : ')
                if end_input and not validate_date(end_input, datetime_format):
                    print('Invalid datetime, ensure YYYY-MM-DD HH:MM:SS')
                    continue
                else:
                    end_date = end_input
                    break

    # Start/end date required if no period
    else:
        if 'd' in interval:
            while True:
                print('\n')
                start_input = input('Start date (YYYY-MM-DD): ')
                if not validate_date(start_input, date_format):
                    print('Invalid date, ensure YYYY-MM-DD format')
                    continue
                else:
                    start_date = start_input
                    break

            while True:
                print('\n')
                end_input = input('End date (YYYY-MM-DD): ')
                if not validate_date(end_input, date_format):
                    print('Invalid date, ensure YYYY-MM-DD format')
                    continue
                else:
                    end_date = end_input
                    break
        else:
            while True:
                start_input = input('Start Datetime (YYYY-MM-DD HH:MM:SS) : ')
                if not validate_date(start_input, datetime_format):
                    print('Invalid datetime, ensure YYYY-MM-DD HH:MM:SS')
                    continue
                else:
                    start_date = start_input
                    break

            while True:
                end_input = input('End Datetime (YYYY-MM-DD HH:MM:SS) : ')
                if not validate_date(end_input, datetime_format):
                    print('Invalid datetime, ensure YYYY-MM-DD HH:MM:SS')
                    continue
                else:
                    end_date = end_input
                    break

    # Download OHLC data, save as CSV
    print('\n')
    print('Downloading OHLC data...','\n')

    subdir = (
        'm5' if interval == '5m' 
        else 'm15' if interval == '15m' 
        else 'm30' if interval == '30m'
        else 'h1' if interval == '1h'
        else 'h4' if interval == '4h'
        else 'd1' if interval == '1d'
        else None # TO DO: create function for creating new folder for new interval
        )

    if single_multi == 2:

        for symbol in symbols:
            if source == 1:
                df = OHLC(symbol, period, interval, start_date, end_date).from_alpaca()
            elif source == 2:
                df = OHLC(symbol, period, interval, start_date, end_date).from_yfinance()

            if start_date and end_date:
                df.to_csv(f'ohlc_csv/{subdir}/{symbol}_{start_date[:4]}{start_date[5:7]}_{end_date[:4]}{end_date[5:7]}_{interval}.csv')
            elif not start_date and end_date:
                df.to_csv(f'ohlc_csv/{subdir}/{symbol}_{end_date[:4]}{end_date[5:7]}_{period}_{interval}.csv')
            else:
                df.to_csv(f'ohlc_csv/{subdir}/{symbol}_{period}_{interval}.csv')

    else:
        if int(source) == 1:
            df = OHLC(symbol, period, interval, start_date, end_date).from_alpaca()
        elif int(source) == 2:
            df = OHLC(symbol, period, interval, start_date, end_date).from_yfinance()

        if start_date != None and end_date != None:
            df.to_csv(f'ohlc_csv/{subdir}/{symbol}_{start_date[:4]}{start_date[5:7]}_{end_date[:4]}{end_date[5:7]}_{interval}.csv')
        elif start_date == None and end_date != None:
            df.to_csv(f'ohlc_csv/{subdir}/{symbol}_{end_date[:4]}{end_date[5:7]}_{period}_{interval}.csv')
        else:
            df.to_csv(f'ohlc_csv/{subdir}/{symbol}_{period}_{interval}.csv')

    print("OHLC data downloaded successfully!")


if __name__ == "__main__":
    main()

