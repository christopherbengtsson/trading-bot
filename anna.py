from datetime import datetime
from binance.enums import SIDE_BUY, SIDE_SELL
from telegram_alert import send_alert
import schedule
import time
import os
from dotenv import load_dotenv
from termcolor import cprint
from binance_client import BinanceClient
import strategy as st
import json

load_dotenv()


def run_bot(bc: BinanceClient, symbol_info):
    symbol = symbol_info['symbol']

    data = bc.fetch_data(symbol)
    if len(data) > 0:
        df = st.set_up_dataframe(data)
        should_buy = st.check_buy_signal(df)
        if should_buy:
            market_order = bc.create_market_order(
                SIDE_BUY, symbol_info)
            if market_order:
                cprint(f"*** Market order placed for {symbol}, making a OCO order ***",
                       'green', attrs=['blink'])
                send_alert(
                    f'Market order placed for {symbol}, making a OCO order')
                oco_order_success = bc.create_oco_order(
                    SIDE_SELL, market_order, df, symbol_info)
                if oco_order_success:
                    cprint(f"*** OCO order placed for {symbol} ***",
                           'green', attrs=['blink'])
                    send_alert(f'OCO order placed for {symbol}')


def for_each_crypto(bc: BinanceClient):
    is_weekday = datetime.today().weekday() < 5

    if os.environ.get('RUN_ANNA') == 'True' and is_weekday:
        pairs = json.loads(os.environ.get('CRYPTOS'))
        for pair in pairs:
            symbol_info = bc.get_symbol_info(pair)
            if symbol_info and symbol_info['ocoAllowed']:
                run_bot(bc, symbol_info)
    else:
        print("Anna is resting...")


if __name__ == '__main__':
    bc = BinanceClient()

    for_each_crypto(bc)

    if os.environ.get('DEV') != 'True':
        schedule.every(1).minutes.do(lambda: for_each_crypto(bc))

        while True:
            schedule.run_pending()
            time.sleep(1)
