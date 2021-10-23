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

        alert_side = 'sell' if side == SIDE_SELL else 'buy'

        if order_type == ORDER_TYPE_MARKET and current_order_status == ORDER_STATUS_FILLED:
            send_alert(f"""<strong><u>Market {alert_side} order {symbol}</u></strong>
<pre>
Amount: {last_executed_price}
Quantity: {order_quantity}
Price: {quote_Order_Qty}
</pre>""")

        elif order_type == ORDER_TYPE_STOP_LOSS_LIMIT:
            # Stop loss
            if current_order_status == 'NEW':
                send_alert(f"""<i><u>Stoploss {symbol}</u></i>

<pre>Trigger Price: {stop_price}
Stoploss: {order_price}</pre>""")

            elif current_order_status == ORDER_STATUS_FILLED:
                send_alert(f"""⛔️ <strong><u>Stoploss executed {symbol}</u></strong> ⛔️

<pre>Price: {last_executed_price}</pre>""")

        elif order_type == ORDER_TYPE_LIMIT_MAKER:
            # Take profit
            if current_order_status == 'NEW':
                send_alert(f"""<i><u>Take Profit {symbol}</u></i>

<pre>Target: {order_price}</pre>""")

            elif current_order_status == ORDER_STATUS_FILLED:
                send_alert(f"""✅ <strong><u>Take Profit executed {symbol}</u></strong> ✅

<pre>Price: {last_executed_price}</pre>""")

    elif msg['e'] == 'listStatus':
        print_json(msg)

        symbol = msg["s"]
        if msg['l'] == 'EXEC_STARTED':
            send_alert(
                f"""<i>OCO order <u>PLACED</u> for <u>{symbol}</u></i>""")
        elif msg['l'] == 'ALL_DONE':
            send_alert(f"""<i>OCO order <u>DONE</u> for <u>{symbol}</u></i>""")
        elif msg['l'] == 'RESPONSE':
            reject = msg['r']
            send_alert(f"""Something went bad with OCO order:

{reject}""", True)
