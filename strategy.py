from binance.enums import SIDE_BUY, SIDE_SELL
import pandas as pd
from ta import trend
from ta import volatility
from termcolor import cprint


def get_indicators(close):
    macd_line = trend.macd(close=close)
    macd_signal_line = trend.macd_signal(close=close)
    macd_histogram = trend.macd_diff(close=close)

    ema200 = trend.ema_indicator(close=close, window=200)

    atr = volatility.average_true_range()

    return macd_line, macd_signal_line, macd_histogram, ema200, atr


def set_up_dataframe(data):
    try:
        df = pd.DataFrame(data, dtype=float, columns=['date',
                                                      'open', 'high', 'low', 'close'])

        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(
            df.index, unit='ms', utc=True, infer_datetime_format=True)

        df['macd_line'], df['macd_signal_line'], df['macd_histogram'], df['ema200'], df['atr'] = get_indicators(
            df['close'])

        return df
    except:
        cprint("Failed setting up DateFrame", 'red', attrs=['bold'])
        return pd.DataFrame()


def check_strategy_signal(df):
    last_closed_index = len(df) - 2
    previous_closed_index = last_closed_index - 1

    last_closed_price = df['close'][last_closed_index]
    last_closed_ema = df['ema200'][last_closed_index]

    last_closed_macd_line = df['macd_line'][last_closed_index]
    last_closed_macd_signal_line = df['macd_signal_line'][last_closed_index]

    previous_closed_macd_line = df['macd_line'][previous_closed_index]
    previous_closed_macd_signal_line = df['macd_signal_line'][previous_closed_index]

    # Check if in a uptrend
    if last_closed_price > last_closed_ema:
        # Check for MACD crossover above 0 line
        if previous_closed_macd_line <= previous_closed_macd_signal_line and last_closed_macd_line > last_closed_macd_signal_line and last_closed_macd_line < 0:
            return SIDE_BUY
    # Check if in a downtrend
    elif last_closed_price < last_closed_ema:
        # Check for MACD crossover beneath 0 line
        if previous_closed_macd_line >= previous_closed_macd_signal_line and last_closed_macd_line < last_closed_macd_signal_line and last_closed_macd_line > 0:
            return SIDE_SELL
