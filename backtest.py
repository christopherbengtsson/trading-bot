import os
from binance_client import BinanceClient
from binance.enums import KLINE_INTERVAL_1MINUTE, SIDE_BUY, SIDE_SELL
from strategy import check_buy_signal, set_up_dataframe
from termcolor import cprint
from dotenv import load_dotenv

load_dotenv()
symbol = 'BTCUSDT'

# in_position = False

buy_price = 0
qty = 0
stopPrice = 0
stopLimitPrice = 0
price = 0

buys = 0
sells = 0

asset_usdt = 50
asset_btc = 50


def test_happy_path(df, symbol_info):
    for index in range(1, len(df)):
        two_latest_candles = df.iloc[[index - 1, index]]
        should_buy = check_buy_signal(two_latest_candles)

        if should_buy:
            market_order = bc.create_market_order(
                side=SIDE_BUY, symbol_info=symbol_info)
            if market_order:
                cprint("*** Market order placed, making a OCO order ***",
                       'green', attrs=['blink'])
                oco_order_success = bc.create_oco_order(
                    SIDE_SELL, market_order, df, symbol_info)
                if oco_order_success:
                    cprint("*** OCO order placed ***",
                           'green', attrs=['blink'])
            break


def run_test_bot(bc: BinanceClient):
    symbol_info = bc.get_symbol_info(symbol)
    data = bc.fetch_data(symbol, backtest=True,
                         interval=KLINE_INTERVAL_1MINUTE)
    df = set_up_dataframe(data).dropna()
    # print(df)
    test_happy_path(df, symbol_info)
    # print_json(res)


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


if __name__ == '__main__':
    clearConsole()
    bc = BinanceClient()
    run_test_bot(bc)
