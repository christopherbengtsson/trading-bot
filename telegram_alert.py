import os
from binance.enums import ORDER_TYPE_LIMIT_MAKER, ORDER_TYPE_STOP_LOSS_LIMIT
from telegram import Update, ForceReply, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext


def send_alert(message, error=False):
    if error:
        bot_message = f"""🔴🔴🔴 <strong><u>ERROR</u></strong> 🔴🔴🔴

<pre>{str(message)}</pre>"""

    else:
        bot_message = message

    bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))

    bot.send_message(chat_id=os.environ.get(
        'TELEGRAM_CHAT_ID'), text=bot_message, parse_mode=ParseMode.HTML)

# Define a few command handlers. These usually take the two arguments update and
# context.


class Bot():
    def __init__(self, bc) -> None:

        self.bc = bc
        # Create the Updater and pass it your bot's token.
        updater = Updater(token=os.environ.get('TELEGRAM_TOKEN'))

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler(
            "active_orders", self.active_orders_command))

        # Start the Bot
        updater.start_polling()

    def active_orders_command(self, update: Update, context: CallbackContext) -> None:
        message = ""
        orders = self.bc.get_open_orders()
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
