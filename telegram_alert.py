import os
from binance.enums import ORDER_TYPE_LIMIT_MAKER, ORDER_TYPE_STOP_LOSS_LIMIT
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# from heroku import HerokuClient


def send_alert(message, error=False):
    if error:
        bot_message = f"""🔴🔴🔴 <strong><u>ERROR</u></strong> 🔴🔴🔴

<pre>{str(message)}</pre>"""

    else:
        bot_message = message

    bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))

    bot.send_message(chat_id=os.environ.get(
        'TELEGRAM_CHAT_ID'), text=bot_message, parse_mode=ParseMode.HTML)


class AnnaTelegramBot():
    def __init__(self, bc) -> None:
        # BinanceClient instance
        self.bc = bc
        # self.hc = HerokuClient()

        updater = Updater(token=os.environ.get('TELEGRAM_TOKEN'))

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler(
            "active_orders", self.active_orders_command))

        updater.start_polling()

    # def start_anna(self, update: Update, context: CallbackContext):
    #     self.hc.start_bot()

    # def stop_anna(self, update: Update, context: CallbackContext):
    #     self.hc.stop_bot()

    # def set_config_vars(self, update: Update, context: CallbackContext):
    #     pass

    def active_orders_command(self, update: Update, context: CallbackContext) -> None:
        message = ""
        orders = self.bc.get_open_orders()
        if len(orders) == 0:
            update.message.reply_text('No active orders')
        else:
            i = 0
            for order in orders:
                i += 1
                row_break = '\n\n' if i > 1 else ""
                if order['type'] == ORDER_TYPE_STOP_LOSS_LIMIT:
                    message += f"""{row_break}<strong><u>{order['symbol']}</u></strong>
<pre>
Trigger Price: {order['stopPrice']}
Stoploss: {order['price']}</pre>"""
                elif order['type'] == ORDER_TYPE_LIMIT_MAKER:
                    message += f"""{row_break}<strong><u>{order['symbol']}</u></strong>
<pre>
Target: {order['price']}</pre>"""

            update.message.reply_html(message)
