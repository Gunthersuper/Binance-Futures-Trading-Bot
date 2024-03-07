**Binance Futures Trading Bot** 

USDT-Perpetual contracts only. 

1. Installing: `pip install -r requirements.txt`

2. Add API-key and Secret key to `keys.py`. You can get it from https://www.binance.com/en/my/settings/api-management

3. Customize your strategies as you want. Use `macd.py` and `rsi.py` as examples

**How to make your own script:**

Import all the needed packages:
```
from helper import Binance
from keys import api, secret
import ta
import pandas as pd
from time import sleep
```

Create a new instance with your API keys:
```
session = Binance(api, secret)
```

Make your own strategy with Buy or Sell signal:

```
def macd_ema(symbol):
    kl = session.klines(symbol, '15m')
    macd = ta.trend.macd_diff(kl.Close)
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        return 'buy'
    if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        return 'sell'
```
`kl` is candlesticks for `symbol` and `'15m'` timeframe. You can change timeframe to '1m', '3m', '5m', '15m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1m'.
`kl` looks like: 
```
Time                 Open    High     Low   Close      Volume
2024-03-02 08:15:00  0.6294  0.6302  0.6207  0.6281  34957767.3
2024-03-02 08:30:00  0.6281  0.6327  0.6271  0.6324  21156707.0
2024-03-02 08:45:00  0.6325  0.6362  0.6318  0.6328  27640540.6
2024-03-02 09:00:00  0.6327  0.6358  0.6302  0.6347  23539850.1
2024-03-02 09:15:00  0.6346  0.6362  0.6286  0.6345  41063211.7
...                     ...     ...     ...     ...         ...
2024-03-07 12:00:00  0.6228  0.6255  0.6217  0.6247  12338957.5
2024-03-07 12:15:00  0.6247  0.6259  0.6233  0.6247  15187530.5
2024-03-07 12:30:00  0.6246  0.6252  0.6232  0.6236  10026492.3
2024-03-07 12:45:00  0.6235  0.6237  0.6194  0.6212  16350902.4
2024-03-07 13:00:00  0.6212  0.6215  0.6181  0.6183   9748855.8

```
I use TA library for technical analysis. More info here - https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html or https://github.com/bukosabino/ta

Then make some config you want. Its like: `tp` (Take Profit), `sl` (Stop Loss), `qty` is quantity for one order in USDT. 
```
tp = 0.012
sl = 0.009
qty = 10
leverage = 10
mode = 'ISOLATED'
max_pos = 50
```

Get all tickers (symbols) form the market:
```
symbols = session.get_tickers_usdt()
```

Execute script:
```
while True:
    try:
        balance = session.get_balance_usdt()
        # qty = balance * 0.3
        print(f'Balance: {round(balance, 3)} USDT')
        positions = session.get_positions()
        print(f'{len(positions)} Positions: {positions}')
        orders = session.check_orders()
        
        for elem in orders:
            if not elem in positions:
                session.close_open_orders(elem)

        for symbol in symbols:
            positions = session.get_positions()
            if len(positions) >= max_pos:
                break
            sign = macd(symbol)
            if sign is not None and not symbol in positions and not symbol in orders:
                print(symbol, sign)
                session.open_order_market(symbol, sign, qty, leverage, mode, tp, sl)
                sleep(1)

        wait = 300
        print(f'Waiting {wait} sec')
        sleep(wait)
    except Exception as err:
        print(err)
        sleep(30)
```
Its an infinite loop, use `try-except` to avoid any cruches.

Get current balance using `session.get_balance_usdt()`. You can set `qty` that depends on the current balance
```
balance = session.get_balance_usdt()
# qty = balance * 0.3
print(f'Balance: {round(balance, 3)} USDT')
```

Get all current positions:
```
positions = session.get_positions()
print(f'{len(positions)} Positions: {positions}')
```

Get all open orders:
```
orders = session.check_orders()
```

Close TP and SL for already closed positions (Binance cant do that automatically):
```
for elem in orders:
    if not elem in positions:
    session.close_open_orders(elem)
```

Checking all symbols from the market:
```
for symbol in symbols:
```

Checking if the script reaches the `max_pos`:
```
positions = session.get_positions()
    if len(positions) >= max_pos:
        break
```

Getting signal for `symbol`:
```
sign = macd(symbol)
```

If there is some signal like 'buy` or `sell`, then place order (buy or sell), and script checks if this symbol isnt in the current position and orders (to avoid mass creatind orders for one symbol)
```
if sign is not None and not symbol in positions and not symbol in orders:
    print(symbol, sign)
    session.open_order_market(symbol, sign, qty, leverage, mode, tp, sl)
    sleep(1)
```
There is only `MARKET` order now. I will add `LIMIT` later.

Wait some time after the script got signals for all symbols.
```
wait = 300
print(f'Waiting {wait} sec')
sleep(wait)
```
After 300 sec the script starts checking signals again.
