from helper import Binance
from keys import api, secret
import ta
import pandas as pd
from time import sleep

session = Binance(api, secret)


def macd_ema(symbol):
    kl = session.klines(symbol, '15m')
    macd = ta.trend.macd_diff(kl.Close)
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        return 'buy'
    if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        return 'sell'


tp = 0.012
sl = 0.009
qty = 10
leverage = 10
mode = 'ISOLATED'
max_pos = 50
symbols = session.get_tickers_usdt()
while True:
    try:
        balance = session.get_balance_usdt()
        # qty = balance * 0.3
        print(f'Balance: {round(balance, 3)} USDT')
        positions = session.get_positions()
        orders = session.check_orders()
        print(f'{len(positions)} Positions: {positions}')

        for elem in orders:
            if not elem in positions:
                session.close_open_orders(elem)

        for symbol in symbols:
            positions = session.get_positions()
            if len(positions) >= max_pos:
                break
            sign = macd_ema(symbol)
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
