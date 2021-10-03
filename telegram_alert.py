import telegram
import os


def send_alert(message, error=False):
    if error:
        bot_message = '🔴🔴🔴 ' + 'ERROR' + ' 🔴🔴🔴\n\n' + str(message)
    else:
        bot_message = message
    bot = telegram.Bot(token=os.environ.get('TELEGRAM_TOKEN'))
    bot.sendMessage(chat_id=os.environ.get(
        'TELEGRAM_CHAT_ID'), text=bot_message)
