from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.historical import StockHistoricalDataClient 


def authenticate_alpaca(env_path: str) -> None:
    """
    Asks user for API and Secret keys for alpaca_py API. Tests the keys by making a simple request.
    Creates .env file for keys in package folder if keys are valid.
    """
    authenticated = False
    while authenticated == False:
        print('\n')
        api_key = input("Enter alpaca-py API key: ")
        print('\n')
        secret_key = input("Enter alpaca-py SECRET key: ")
        print('\n')

        # Test key validity
        client = StockHistoricalDataClient(api_key, secret_key)
        try:
            request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY"])
            latest_quote = client.get_stock_latest_quote(request_params)
        except Exception as e:
            print('Error. Possibly invalid keys. Check that you have entered valid keys, or that they have been entered correctly')
            continue
        else:
            print("API and Secret keys authenticated!\n")
            authenticated = True
            # Write keys to .env file
            with open(env_path + '/.env', 'w') as f:
                f.write(f'API_KEY={api_key}\n')
                f.write(f'SECRET_KEY={secret_key}\n')

    print('.env file created successfully')