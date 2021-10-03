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

load_dotenv()


in_position = False


def run_bot(bc: BinanceClient):
    global in_position
    symbol = 'BTCUSDT'

    # TODO When multiple cryptos, filter out unallowed ones
    symbol_info = bc.get_symbol_info(symbol)
    oco_is_allowed = symbol_info['ocoAllowed']

    is_weekday = datetime.today().weekday() < 5

    if os.environ.get('RUN_ANNA') == 'True' and oco_is_allowed and is_weekday:
        data = bc.fetch_data(symbol)
        if len(data) > 0:
            df = st.set_up_dataframe(data)

            should_buy = st.check_buy_signal(df)
            latest_close_price = df['close'][len(df) - 1]
            if should_buy:
                market_order = bc.create_market_order(
                    SIDE_BUY, symbol_info, latest_close_price)
                if market_order:
                    in_position = True
                    cprint("*** Market order placed, making a OCO order ***",
                           'green', attrs=['blink'])
                    send_alert('Market order placed, making a OCO order')
                    oco_order_success = bc.create_oco_order(
                        SIDE_SELL, market_order, df, symbol_info)
                    if oco_order_success:
                        cprint("*** OCO order placed ***",
                               'green', attrs=['blink'])
                        send_alert('OCO order placed')
                        # TODO Look for settled orders - set in_position

    else:
        print("Anna is resting...")


if __name__ == '__main__':
    bc = BinanceClient()

    run_bot(bc)

    if os.environ.get('DEV') != 'True':
        schedule.every(1).minutes.do(lambda: run_bot(bc))

        while True:
            schedule.run_pending()
            time.sleep(1)
