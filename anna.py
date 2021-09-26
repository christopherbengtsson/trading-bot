import pandas as pd
from ta import trend
import schedule
from datetime import datetime
import time
import ccxt
import os
from dotenv import load_dotenv
from termcolor import cprint
import csv

pd.set_option('display.max_rows', None)

load_dotenv()
exchange = ccxt.binance({
    "apiKey": os.environ.get('API_KEY'),
    "secret": os.environ.get('API_SECRET')
})


def get_account_balance(currency):
    try:
        return exchange.fetch_free_balance()[currency]
    except:
        cprint("No balance")


def fetch_data(symbol, timeframe, limit):
    cprint(f"Fetching new bars for {datetime.now().isoformat()}")
    try:
        return exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    except:
        cprint("Failed fetching data", 'red', attrs=['bold'])
        return []


def set_up_dataframe(data):
    try:
        df = pd.DataFrame(data, columns=['timestamp',
                                         'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # MACD
        df['macd_line'] = trend.macd(close=df['close'])
        df['macd_signal_line'] = trend.macd_signal(close=df['close'])
        # df['macd_histogram'] = trend.macd_diff(close=df['close'])

        # 200 EMA
        df['200_ema'] = trend.ema_indicator(close=df['close'], window=200)

        # print(df)

        return df
    except:
        cprint("Failed setting up DateFrame", 'red', attrs=['bold'])
        return pd.DataFrame()


in_position = False


def check_for_signals(df, symbol):
    global in_position

    last_row_index = len(df) - 1
    previous_row_index = last_row_index - 1

    last_row_close = df['close'][last_row_index]
    last_row_ema = df['200_ema'][last_row_index]

    last_row_macd_line = df['macd_line'][last_row_index]
    last_row_macd_signal_line = df['macd_signal_line'][last_row_index]

    previous_row_macd_line = df['macd_line'][previous_row_index]
    previous_row_macd_signal_line = df['macd_signal_line'][previous_row_index]

    amount = 0.006

    if last_row_close > last_row_ema:
        if previous_row_macd_line < previous_row_macd_signal_line and last_row_macd_line > last_row_macd_signal_line and last_row_macd_line < 0:
            if not in_position:
                cprint("*** Buy signal, making an order ***",
                       'green', attrs=['blink'])
                order = exchange.create_market_buy_order(symbol, amount)
                cprint(order)
                in_position = True
            else:
                cprint(
                    "*** Buy Signal but already in position ***", 'yellow', attrs=['bold'])

    elif last_row_close < last_row_ema:
        if previous_row_macd_line > previous_row_macd_signal_line and last_row_macd_line < last_row_macd_signal_line and last_row_macd_line > 0:
            if in_position:
                cprint("*** Sell signal, making an order ***",
                       'green', attrs=['blink'])
                order = exchange.create_market_sell_order(symbol, amount)
                cprint(order)
                in_position = False
            else:
                cprint("*** Sell Signal but not in position ***",
                       'yellow', attrs=['bold'])


def run_bot():
    symbol = 'ETH/EUR'
    timeframe = '30m'
    limit = 300

    if os.environ.get('RUN_ANNA') == 'True':
        data = fetch_data(symbol=symbol, timeframe=timeframe, limit=limit)
        if len(data) > 0:
            df = set_up_dataframe(data)
            check_for_signals(df, symbol)
    else:
        cprint("Anna is resting...")


# print(get_account_balance('EUR'))
schedule.every(1).minutes.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)
