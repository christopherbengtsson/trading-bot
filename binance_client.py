from binance.helpers import round_step_size
from typing import Dict
from utils import print_json
from telegram_alert import send_alert
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime
from termcolor import cprint
import os


class BinanceClient:
    def __init__(self):
        if os.environ.get('DEV') == 'True':
            cprint("*** Using TestNet API ***",
                   'green', attrs=['bold', 'underline'])

            self.client = Client(os.environ.get('API_KEY_TESTNET'),
                                 os.environ.get('API_SECRET_TESTNET'), testnet=True)
        else:
            self.client = Client(os.environ.get('API_KEY'),
                                 os.environ.get('API_SECRET'))

    def fetch_data(self, symbol, interval=KLINE_INTERVAL_30MINUTE, limit=250, backtest=False):
        try:
            candles: Dict
            if not backtest:
                print(
                    f"Fetching new candles for {symbol} {datetime.now().isoformat()}")
                candles = self.client.get_klines(
                    symbol=symbol, interval=interval, limit=limit)
            else:
                print(
                    f"Fetching new historical candles for {symbol} {datetime.now().isoformat()}")
                candles = self.client.get_historical_klines(
                    symbol=symbol, interval=interval, limit=limit, start_str="1 Jan, 2021")
            for line in candles:
                del line[5:]
            return candles
        except BinanceAPIException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return {}
        except BinanceOrderException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return {}

    def get_symbol_info(self, symbol):
        try:
            return self.client.get_symbol_info(symbol)
        except BinanceAPIException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False
        except BinanceOrderException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False

    def get_balance(self, asset):
        try:
            return self.client.get_asset_balance(asset=asset)
        except BinanceAPIException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False
        except BinanceOrderException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False

    def get_filter(self, filters, filter_type, filter_prop, get_float=False):
        for f in filters:
            if f['filterType'] == filter_type:
                result = (f[filter_prop])
                return float(result) if get_float else result

    def get_closest_swing_low(self, df):
        lowest_histo = 0
        lowest_price = 0

        # Trying to find the latest swing low or pullback of trend
        for current in range(1, len(df.index)):
            # reverse column in dataframe and get index. So latest first.
            previous_histo = df[::-1]['macd_histogram'][current]
            previous_lowest_price = float(df[::-1]['low'][current])

            # check if first iteration or if hiso is positive, e.g. in a late buy
            if lowest_histo == 0 and previous_histo >= 0:
                continue
            elif lowest_histo < 0 and previous_histo >= 0:
                break

            if previous_lowest_price < lowest_price:
                lowest_histo = previous_histo
                lowest_price = previous_lowest_price
            elif lowest_price == 0:
                lowest_price = previous_lowest_price

        return lowest_price

    def create_market_order(self, side, symbol_info, latest_close_price):
        # TODO: Market or limit order?

        try:
            symbol = symbol_info['symbol']
            quote_amount = float(os.environ.get('MAX_USDT_PRICE'))  # UDST

            filters = symbol_info['filters']
            tick_size = self.get_filter(
                filters, 'PRICE_FILTER', 'tickSize', True)
            req_price = round_step_size(quote_amount, tick_size)

            if side == SIDE_BUY:
                order = self.client.order_market_buy(
                    symbol=symbol, quoteOrderQty=req_price)
                print_json(order)
                return order
            # elif side == SIDE_SELL:
            #     order = self.client.order_market_sell(
            #         symbol=symbol, quantity=qty)
            #     print_json(order)
            #     return order

            return False

        except BinanceAPIException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False
        except BinanceOrderException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False

    def create_oco_order(self, side, market_order, df, symbol_info):
        symbol = symbol_info['symbol']
        filters = symbol_info['filters']
        market_order_fills = market_order.get('fills')
        market_order_qty = float(market_order.get('executedQty'))
        purchase_price = sum(
            [float(f['price']) * (float(f['qty']) / market_order_qty) for f in market_order_fills])
        tick_size = self.get_filter(
            filters, 'PRICE_FILTER', 'tickSize', True)

        swing_low = self.get_closest_swing_low(df)
        # *** Stop loss - lower than bought price ***
        # Long: set below the pullback of the trend
        # Short: set above the pullback of the trend

        # stop signal
        stopPrice = purchase_price
        # actual sell price. To be more secure, set lower than stopPrice
        stopLimitPrice = swing_low

        # *** Take profit (higher than bought price) ***
        # Set 1.5x the size of the stop loss
        req_price = stopPrice + ((stopPrice - stopLimitPrice) * 1.5)
        take_profit = round_step_size(req_price, tick_size)

        # Price Restrictions:
        # SELL: Limit Price > Last Price > Stop Price
        # BUY: Limit Price < Last Price < Stop Price
        if take_profit > stopPrice and stopPrice > stopLimitPrice and stopLimitPrice > 0:
            try:
                # creates two orders, one take profit and one stop-loss
                cprint(
                    f"Sending OCO order: take profit: {take_profit}, stopPrice: {stopPrice}, stopLimitPrice: {stopLimitPrice}, qty: {market_order_qty}", 'green', attrs=['bold'])
                send_alert(
                    f"Sending OCO order: take profit: {take_profit}, stopPrice: {stopPrice}, stopLimitPrice: {stopLimitPrice}")
                order = self.client.create_oco_order(
                    symbol=symbol,
                    side=side,  # SELL/BUY
                    quantity=market_order_qty,
                    price=str(take_profit),
                    stopPrice=str(stopPrice),
                    stopLimitPrice=str(stopLimitPrice),
                    stopLimitTimeInForce=TIME_IN_FORCE_GTC
                )
                print_json(order)
                return True
            except BinanceAPIException as e:
                cprint(e, 'red', attrs=['bold'])
                send_alert(e, True)
                return False
            except BinanceOrderException as e:
                cprint(e, 'red', attrs=['bold'])
                send_alert(e, True)
                return False
        else:
            cprint(
                f'OCO order setup is incorrent: take profit: {take_profit}, stopPrice: {stopPrice}, stopLimitPrice: {stopLimitPrice}', 'red', attrs=['bold'])

    def validate(self, symbol, side, type, price, qty):
        order = self.client.create_test_order(
            symbol=symbol,
            side=side,
            type=type,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=qty,
            price=price
        )
        print(order)

    def topup_bnb(self, min_balance=1.0, topup=2.5, symbol='BNBUSDT'):
        ''' Top up BNB balance if it drops below minimum specified balance '''

        bnb_balance = self.client.get_asset_balance(asset='BNB')
        bnb_balance = float(bnb_balance['free'])
        if bnb_balance < min_balance:
            qty = round(topup - bnb_balance, 5)
            print(f"Quantity to topup: {qty}")
            order = self.client.order_market_buy(symbol=symbol, quantity=qty)
            return order
        return False
