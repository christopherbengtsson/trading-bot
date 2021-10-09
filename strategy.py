from binance.enums import SIDE_BUY, SIDE_SELL
import pandas as pd
from ta import trend
from termcolor import cprint


def get_indicators(close):
    macd_line = trend.macd(close=close)
    macd_signal_line = trend.macd_signal(close=close)
    macd_histogram = trend.macd_diff(close=close)

    ema200 = trend.ema_indicator(close=close, window=200)

    return macd_line, macd_signal_line, macd_histogram, ema200


def set_up_dataframe(data):
    try:
        df = pd.DataFrame(data, dtype=float, columns=['date',
                                                      'open', 'high', 'low', 'close'])

        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(
            df.index, unit='ms', utc=True, infer_datetime_format=True)

        df['macd_line'], df['macd_signal_line'], df['macd_histogram'], df['ema200'] = get_indicators(
            df['close'])

        return df
    except:
        cprint("Failed setting up DateFrame", 'red', attrs=['bold'])
        return pd.DataFrame()


def check_strategy_signal(df):
    last_row_index = len(df) - 1
    previous_row_index = last_row_index - 1

    last_row_close = df['close'][last_row_index]
    last_row_ema = df['ema200'][last_row_index]

    last_row_macd_line = df['macd_line'][last_row_index]
    last_row_macd_signal_line = df['macd_signal_line'][last_row_index]

    previous_row_macd_line = df['macd_line'][previous_row_index]
    previous_row_macd_signal_line = df['macd_signal_line'][previous_row_index]

    # Check if in a uptrend
    if last_row_close > last_row_ema:
        # Check for MACD crossover above 0 line
        if previous_row_macd_line <= previous_row_macd_signal_line and last_row_macd_line > last_row_macd_signal_line and last_row_macd_line < 0:
            # Buy
            # cprint("*** Strategy buy signal ***", 'green', attrs=['blink'])
            return SIDE_BUY
    # Check if in a downtrend
    elif last_row_close < last_row_ema:
        # Check for MACD crossover beneath 0 line
        if previous_row_macd_line >= previous_row_macd_signal_line and last_row_macd_line < last_row_macd_signal_line and last_row_macd_line > 0:
            # Buy
            # cprint("*** Strategy sell signal ***", 'green', attrs=['blink'])
            return SIDE_SELL
