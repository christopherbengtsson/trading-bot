import os
import logging
import traceback
import html
import json
from binance.enums import ORDER_TYPE_LIMIT_MAKER, ORDER_TYPE_STOP_LOSS_LIMIT
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# from heroku import HerokuClient

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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
        print("Starting Telegram Bot...")
        # BinanceClient instance
        self.bc = bc
        # self.hc = HerokuClient()

        updater = Updater(token=os.environ.get('TELEGRAM_TOKEN'))

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler(
            "active_orders", self.active_orders_command))

        dispatcher.add_error_handler(self.error_handler)

        updater.start_polling()

    # def start_anna(self, update: Update, context: CallbackContext):
    #     self.hc.start_bot()

    # def stop_anna(self, update: Update, context: CallbackContext):
    #     self.hc.stop_bot()

    # def set_config_vars(self, update: Update, context: CallbackContext):
    #     pass
    def error_handler(self, update: object, context: CallbackContext) -> None:
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:",
                     exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f'An exception was raised while handling an update\n'
            f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
            '</pre>\n\n'
            f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
            f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )

        # Finally, send the message
        send_alert(message, True)

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
