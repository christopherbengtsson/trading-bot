import telegram
import os


def send_alert(message, error=False):
    if error:
        bot_message = f"""🔴🔴🔴 <strong><u>ERROR</u></strong> 🔴🔴🔴

<pre>{str(message)}</pre>"""

    else:
        bot_message = message

    bot = telegram.Bot(token=os.environ.get('TELEGRAM_TOKEN'))

    bot.send_message(chat_id=os.environ.get(
        'TELEGRAM_CHAT_ID'), text=bot_message, parse_mode=telegram.ParseMode.HTML)
