from binance.enums import SIDE_BUY, SIDE_SELL
import pandas as pd
from ta import trend
from ta import volatility
from termcolor import cprint


def get_indicators(high, low, close):
    macd_line = trend.macd(close)
    macd_signal_line = trend.macd_signal(close)
    macd_histogram = trend.macd_diff(close)

    ema200 = trend.ema_indicator(close, window=200)

    atr = volatility.average_true_range(high, low, close)

    return macd_line, macd_signal_line, macd_histogram, ema200, atr


def set_up_dataframe(data):
    try:
        df = pd.DataFrame(data, dtype=float, columns=['date',
                                                      'open', 'high', 'low', 'close'])

        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(
            df.index, unit='ms', utc=True, infer_datetime_format=True)

        df['macd_line'], df['macd_signal_line'], df['macd_histogram'], df['ema200'], df['atr'] = get_indicators(
            df['high'], df['low'], df['close'])

        return df
    except:
        cprint("Failed setting up DateFrame", 'red', attrs=['bold'])
        return pd.DataFrame()


def check_strategy_signal(df):
    entry_candle_index = len(df) - 1
    last_closed_index = entry_candle_index - 1
    previous_closed_index = last_closed_index - 1

    entry_candle_open = df['open'][entry_candle_index]
    entry_candle_close = df['close'][entry_candle_index]
    entry_candle_ema = df['ema200'][entry_candle_index]

    last_closed_macd_line = df['macd_line'][last_closed_index]
    last_closed_macd_signal_line = df['macd_signal_line'][last_closed_index]

    previous_closed_macd_line = df['macd_line'][previous_closed_index]
    previous_closed_macd_signal_line = df['macd_signal_line'][previous_closed_index]

    # Check candle was opened and closed above EMA 200
    if entry_candle_open > entry_candle_ema and entry_candle_close > entry_candle_ema:
        # Check for MACD crossover above 0 line
        if previous_closed_macd_line <= previous_closed_macd_signal_line and last_closed_macd_line > last_closed_macd_signal_line and last_closed_macd_line < 0:
            return SIDE_BUY

# Buy when the MACD line crosses above the signal line, below the zero line if entry candle is above 200 ema
# Stoploss at the lowest point from last 10 candles
# Set profit target 1.5 times stoploss
