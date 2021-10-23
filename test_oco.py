import os
from binance.helpers import round_step_size
from dotenv import load_dotenv
from binance_client import BinanceClient
from binance.enums import *
import strategy as st
from telegram_alert import send_alert
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


def get_filter(filters, filter_type, filter_prop, get_float=False):
    for f in filters:
        if f['filterType'] == filter_type:
            result = (f[filter_prop])
            return float(result) if get_float else result


if __name__ == '__main__':
    # if os.environ.get('DEV') == 'True':
    bc = BinanceClient()
    symbol = 'ALGOUSDT'
    # cancel_all_orders(bc, symbol)

    symbol_info = bc.get_symbol_info(symbol)
    filters = symbol_info['filters']
    tick_size = get_filter(filters, 'PRICE_FILTER', 'tickSize', True)

    data = bc.fetch_data(symbol)
    df = st.set_up_dataframe(data)

    low = df.tail(11)['low'].min()
    stopLimitPrice = round_step_size(low, tick_size)

    atr_at_lowest = float()
    for row in df.tail(11).itertuples():
        if(row.low == low):
            atr_at_lowest = row.atr

    stopPrice = round_step_size(
        stopLimitPrice + (tick_size * atr_at_lowest), tick_size)

    print('stopPrice', stopPrice)
    print('stopLimitPrice', stopLimitPrice)
    print('tick_size', tick_size)
    print('atr_at_lowest', atr_at_lowest)
    print(stopLimitPrice+(tick_size * 500))


alert_side = 'buy'
last_executed_price = "4041.16000000"
order_quantity = "0.003700000"
quote_Order_Qty = "15.000000000"

order_price = "6463.3113"
stop_price = "5976.9987"

send_alert(f"""<strong><u>Market {alert_side} order {symbol}</u></strong>
<pre>
Amount: {last_executed_price}
Quantity: {order_quantity}
Price: {quote_Order_Qty}
</pre>""")

send_alert(f"""<i><u>Stoploss {symbol}</u></i>

<pre>Trigger Price: {stop_price}
Stoploss: {order_price}</pre>""")

send_alert(f"""⛔️ <strong><u>Stoploss executed {symbol}</u></strong> ⛔️

<pre>Price: {last_executed_price}</pre>""")

send_alert(f"""<i><u>Take Profit {symbol}</u></i>

<pre>Target: {order_price}</pre>""")

send_alert(f"""✅ <strong><u>Take Profit executed {symbol}</u></strong> ✅

<pre>Price: {last_executed_price}</pre>""")

send_alert(f"""<i>OCO order <u>PLACED</u> for <u>{symbol}</u></i>""")
send_alert(f"""<i>OCO order <u>DONE</u> for <u>{symbol}</u></i>""")
reject = 'nein nein nein'
send_alert(
    f"""Something went bad with OCO order:

{reject}""", True)


#         send_alert(f"""<strong><u>Market {alert_side} order {symbol}</u></strong>
# <pre>
# Amount: {last_executed_price}
# Quantity: {order_quantity}
# Price: {quote_Order_Qty}
# </pre>""")


#     send_alert("""<b>bold</b>, <strong>bold</strong>
# <i>italic</i>, <em>italic</em>
# <u>underline</u>, <ins>underline</ins>
# <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
# <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
# <a href="http://www.example.com/">inline URL</a>
# <a href="tg://user?id=123456789">inline mention of a user</a>
# <code>inline fixed-width code</code>
# <pre>pre-formatted fixed-width code block</pre>
# <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>""")
# do something

# market_order = bc.create_market_order(SIDE_BUY, symbol_info)
# market_order_fills = market_order.get('fills')
# market_order_qty = float(market_order.get('executedQty'))
# purchase_price = sum(
#     [float(f['price']) * (float(f['qty']) / market_order_qty) for f in market_order_fills])

# print(f'Market order bought at {purchase_price}')

# oco = bc.create_oco_order(SIDE_SELL, market_order, df, symbol_info)
