from telegram_alert import send_alert
from binance.enums import *

from utils import print_json


def handle_ws_messages(msg):
    if msg['e'] == 'executionReport':
        print_json(msg)
        event_type = msg["e"]
        event_time = msg["E"]
        symbol = msg["s"]
        client_order_ID = msg["c"]
        side = msg["S"]
        order_type = msg["o"]
        time_in_force = msg["f"]
        order_quantity = msg["q"]
        order_price = msg["p"]
        stop_price = msg["P"]
        iceberg_quantity = msg["F"]
        orderListId = msg["g"]
        # This is the ID of the order being canceled
        original_client_order_ID = msg["C"]
        current_execution_type = msg["x"]
        current_order_status = msg["X"]
        order_reject_reason = msg["r"]  # will be an error code
        order_ID = msg["i"]
        last_executed_quantity = msg["l"]
        cumulative_filled_quantity = msg["z"]
        last_executed_price = msg["L"]
        commission_amount = msg["n"]
        commission_asset = msg["N"]
        transaction_time = msg["T"]
        trade_ID = msg["t"]
        ignore = msg["I"]
        is_the_order_on_the_book = msg["w"]
        is_this_trade_the_maker_side = msg["m"]
        ignore = msg["M"]
        order_creation_time = msg["O"]
        # (i.e. lastPrice * lastQty)
        cumulative_quote_asset_transacted_quantity = msg["Z"]
        last_quote_asset_transacted_quantity = msg["Y"]
        quote_Order_Qty = msg["Q"]
        alert_side = 'sold' if side == SIDE_SELL else 'bought'
        if order_type == ORDER_TYPE_MARKET and current_order_status == ORDER_STATUS_FILLED:
            send_alert(
                f'Market order ID {order_ID} for {symbol} filled, {alert_side} {order_quantity} for {last_executed_price} at a total price of {quote_Order_Qty}')
        elif order_type == ORDER_TYPE_STOP_LOSS_LIMIT:
            # Stop loss
            if current_order_status == 'NEW':
                send_alert(
                    f'Stop loss order ID {order_ID} for {symbol} placed. Trigger price: {order_price}, stop loss: {stop_price}')
            elif current_order_status == ORDER_STATUS_FILLED:
                send_alert(
                    f'OCO order ID {order_ID} for {symbol} {alert_side} at stop loss at {last_executed_price}')
        elif order_type == ORDER_TYPE_LIMIT_MAKER:
            # Take profit
            if current_order_status == 'NEW':
                send_alert(
                    f'Profit order ID {order_ID} placed for {symbol}. Target is {order_price}')
            elif current_order_status == ORDER_STATUS_FILLED:
                send_alert(
                    f'OCO order ID {order_ID} for {symbol} {alert_side} at profit target at {last_executed_price}')

    elif msg['e'] == 'listStatus':
        print_json(msg)
        orders = msg['O']
        orderId1 = orders[0]['i']
        orderId2 = orders[1]['i']
        if msg['l'] == 'EXEC_STARTED':
            send_alert(
                f'OCO order placed. Order IDs {orderId1} and {orderId2}')
        elif msg['l'] == 'ALL_DONE':
            send_alert(
                f'OCO order DONE. Order IDs {orderId1} and {orderId2}')
        elif msg['l'] == 'RESPONSE':
            reject = msg['r']
            send_alert(
                f'Something went bad with OCO order: {reject}', True)
