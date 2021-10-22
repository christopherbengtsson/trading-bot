from datetime import datetime
from binance.enums import SIDE_BUY, SIDE_SELL
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
        print(df.tail(3))
        signal = st.check_strategy_signal(df)

        if signal == SIDE_SELL:
            market_order = bc.create_market_order(
                signal, symbol_info)

        elif signal == SIDE_BUY:
            orders = bc.get_open_orders(symbol)

            if len(orders) > 0:
                print(f'Already an active order for {symbol}, aborting market buy')
                return
        else:
            return

        market_order = bc.create_market_order(
            signal, symbol_info)

        if market_order:
            cprint(f"*** Market {signal} order placed for {symbol} ***",
                   'green', attrs=['blink'])

            if signal == SIDE_BUY:
                cprint(f"*** Creating OCO order for {symbol} ***",
                       'green', attrs=['blink'])

                oco_order_success = bc.create_oco_order(
                    SIDE_SELL, market_order, df, symbol_info)

                if oco_order_success:
                    cprint(f"*** OCO order placed for {symbol} ***",
                           'green', attrs=['blink'])


def for_each_crypto(bc: BinanceClient):
    is_weekday = datetime.today().weekday() < 5

    if os.environ.get('RUN_ANNA') == 'True' and is_weekday:
        pairs = json.loads(os.environ.get('CRYPTOS'))

        for pair in pairs:
            symbol_info = bc.get_symbol_info(pair)

            if symbol_info and symbol_info['ocoAllowed']:
                run_bot(bc, symbol_info)
    else:
        if not is_weekday:
            print("Anna doesn't work on weekends...")
        else:
            print("Anna is resting...")


if __name__ == '__main__':
    bc = BinanceClient()

    for_each_crypto(bc)

    if os.environ.get('DEV') != 'True':
        schedule.every().hour.at("00:05").do(lambda: for_each_crypto(bc))
        schedule.every().hour.at("30:05").do(lambda: for_each_crypto(bc))

        while True:
            schedule.run_pending()
            time.sleep(1)
