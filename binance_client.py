from binance.helpers import round_step_size
from typing import Dict
from binance import ThreadedWebsocketManager
from telegram_alert import send_alert
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime
from termcolor import cprint
import os
import json
from ws_message_handler import handle_ws_messages


ATR_MULTIPLIER = float(os.environ.get('ATR_MULTIPLIER'))
RISK_REWARD_RATIO = float(os.environ.get('RISK_REWARD_RATIO'))


class BinanceClient:
    def __init__(self):
        testnet = os.environ.get('DEV') == 'True'

        if testnet:
            cprint("*** Using TestNet API ***",
                   'green', attrs=['bold', 'underline'])

            api_key = os.environ.get('API_KEY_TESTNET')
            api_secret = os.environ.get('API_SECRET_TESTNET')
        else:
            api_key = os.environ.get('API_KEY')
            api_secret = os.environ.get('API_SECRET')

        self.client = Client(api_key, api_secret,
                             testnet=testnet)
        self.twm = ThreadedWebsocketManager(
            api_key=api_key, api_secret=api_secret, testnet=testnet)

        self.latest_transactions = []
        self.start_websocket()

    def start_websocket(self):
        self.twm.start()

        self.twm.start_user_socket(callback=handle_ws_messages)

    def get_open_orders(self, symbol):
        try:
            return self.client.get_open_orders(symbol=symbol)
        except BinanceAPIException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return []
        except BinanceOrderException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return []

    def cancel_order_by_id(self, orderId, symbol):
        return self.client.cancel_order(symbol=symbol, orderId=orderId)

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
        for current in range(len(df) - 2, 0, -1):
            # reverse loop, latest first
            previous_histo = float(df['macd_histogram'][current])
            previous_lowest_price = float(df['low'][current])

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

    def get_closest_swing_high(self, df):
        highest_histo = 0
        highest_price = 0

        # Trying to find the latest swing high or pullback of trend
        for current in range(len(df) - 2, 0, -1):
            # reverse loop, latest first
            previous_histo = float(df['macd_histogram'][current])
            previous_highest_price = float(df['high'][current])

            # check if first iteration or if hiso is negative, e.g. in a late sell
            if highest_histo == 0 and previous_histo <= 0:
                continue
            elif highest_histo > 0 and previous_histo <= 0:
                break

            if previous_highest_price > highest_price:
                highest_histo = previous_histo
                highest_price = previous_highest_price
            elif highest_price == 0:
                highest_price = previous_highest_price

        return highest_price

    def create_market_order(self, side, symbol_info):
        try:
            symbol = symbol_info['symbol']
            quote_asset = symbol_info['quoteAsset']
            quote_req_amount = float(os.environ.get('MAX_USDT_PRICE'))  # UDST

            if os.environ.get('PLOT') == 'True':
                balance = 5000
            else:
                balance = float(self.get_balance(quote_asset)['free'])

            if quote_req_amount > balance:
                quote_amount = balance
            else:
                quote_amount = quote_req_amount

            filters = symbol_info['filters']
            tick_size = self.get_filter(
                filters, 'PRICE_FILTER', 'tickSize', True)
            req_price = round_step_size(quote_amount, tick_size)

            if os.environ.get('PLOT') == 'True':
                with open('example_responses.json') as json_file:
                    data = json.load(json_file)
                return data['market_order']

            print('Placing market order...')
            order = self.client.order_market(
                symbol=symbol, quoteOrderQty=req_price, side=side)

            return order

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

        # *** Stop loss - lower than bought price ***
        # Long: set below the pullback of the trend
        # Short: set above the pullback of the trend
        # actual sell price. To be more secure, set lower than stopPrice
        latest_closed_atr = df['atr'][len(df) - 2]

        stopLimitPrice = round_step_size(
            purchase_price - (latest_closed_atr * ATR_MULTIPLIER), tick_size)

        # stop signal
        # +10% of sell price + 2 pips
        stopPrice = round_step_size(
            (stopLimitPrice + ((purchase_price - stopLimitPrice) * 10 / 100)) + (tick_size * 2), tick_size)

        # *** Take profit (higher than bought price) ***
        # Set 1.5x the size of the stop loss
        req_price = 0
        if side == SIDE_SELL:
            req_price = purchase_price + \
                ((purchase_price - stopLimitPrice) * RISK_REWARD_RATIO)
        else:
            req_price = purchase_price + \
                ((stopLimitPrice - purchase_price) * RISK_REWARD_RATIO)
        take_profit = round_step_size(req_price, tick_size)

        if os.environ.get('PLOT') == 'True':
            return take_profit, stopPrice, stopLimitPrice

        # Price Restrictions:
        # SELL: Limit Price > Last Price > Stop Price
        # BUY: Limit Price < Last Price < Stop Price
        try:
            # creates two orders, one take profit and one stop-loss
            cprint(
                f"Sending OCO order: take profit: {take_profit}, stopPrice: {stopPrice}, stopLimitPrice: {stopLimitPrice}, qty: {market_order_qty}", 'green', attrs=['bold'])

            self.client.create_oco_order(
                symbol=symbol,
                side=side,  # SELL/BUY
                quantity=market_order_qty,
                price=str(take_profit),
                stopPrice=str(stopPrice),
                stopLimitPrice=str(stopLimitPrice),
                stopLimitTimeInForce=TIME_IN_FORCE_GTC
            )

            return True
        except BinanceAPIException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False
        except BinanceOrderException as e:
            cprint(e, 'red', attrs=['bold'])
            send_alert(e, True)
            return False

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
