import os
from dotenv import load_dotenv
from binance_client import BinanceClient
from binance.enums import *
import strategy as st
from utils import print_json

load_dotenv()


def cancel_all_orders(bc: BinanceClient, symbol):
    orders = bc.get_open_orders(symbol)
    print_json(orders)
    print(f'{len(orders)} active orders')
    deleted = []
    for order in orders:
        orderId = order['orderId']

        if not orderId in deleted:
            removed = bc.cancel_order_by_id(orderId, symbol)
            deleted.append(orderId)
            print(removed)
    orders = bc.get_open_orders(symbol)
    print(f'{len(orders)} active orders')


if __name__ == '__main__':
    if os.environ.get('DEV') == 'True':
        bc = BinanceClient()
        symbol = 'BTCUSDT'
        cancel_all_orders(bc, symbol)

       

        # symbol_info = bc.get_symbol_info(symbol)

        # data = bc.fetch_data(symbol)
        # df = st.set_up_dataframe(data)

        # market_order = bc.create_market_order(SIDE_BUY, symbol_info)
        # market_order_fills = market_order.get('fills')
        # market_order_qty = float(market_order.get('executedQty'))
        # purchase_price = sum(
        #     [float(f['price']) * (float(f['qty']) / market_order_qty) for f in market_order_fills])

        # print(f'Market order bought at {purchase_price}')

        # oco = bc.create_oco_order(SIDE_SELL, market_order, df, symbol_info)
