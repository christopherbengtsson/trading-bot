from dotenv.main import load_dotenv
import csv
import os
from binance.client import Client
import numpy as np

load_dotenv()
client = Client(os.environ.get('API_KEY_TESTNET'),
                os.environ.get('API_SECRET_TESTNET'), testnet=True)

# csvfile = open('test/unit_data_30min.csv', 'w', newline='')
# candlestick_writer = csv.writer(csvfile, delimiter=',')

candlesticks = client.get_historical_klines(
    "BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Jan, 2020")

for candlestick in candlesticks:
    del candlestick[5:]   
    # candlestick_writer.writerow(candlestick)


np.save('test/unit_data_30min.npy', candlesticks)

# csvfile.close()
