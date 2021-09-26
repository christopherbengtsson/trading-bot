# Trading Bot (Anna)

A crypto trading bot live trading on a Binance account.

## Strategy

- ### Combine short term MACD with long term 200 EMA

Trade with the MACD but make sure we stay in the same direction as the long term trend. Don't trade against the trend

- ### How

1. Indentify the long term trend
   - If price > long term trend == uptrend
   - If price < long term trend == downtrend
2. Look for crossovers from MACD that shows same signals as long term trend

   - If uptrend -> Check for signals when the MACD crosses over above signal line and under zero line
     - Take long position. Stoploss at nearest swing low and profit target at 1.5 x stoploss
   - If downtrend -> Check for signals when the MACD crosses over below signal line and above zero line
     - Take short position. Stoploss at nearest swing high and profit target 1.5 x stoploss

3. TODO: Advanced strategy -> MACD + Price Action
   1. Choose time frame, e.g. 4h
   2. Identify a key level (resistens or support) within this time frame
   3. Expect a double top (a 2nd touch on key level)
   4. Go down two time frames (2h in this case)
   5. Wait for crossover on MACD to confirm reversal
   6. Take position

## Dev

Create a .env file and add following props:

- API_KEY=your-api-key
- API_SECRET=your-api-secret
- RUN_ANNA=True

run `pip install -r requirements.txt`

run `python3 anna.py`
