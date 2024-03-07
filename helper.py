from binance.um_futures import UMFutures
import pandas as pd
from time import sleep
from binance.error import ClientError


class Binance:
    def __init__(self, api, secret):
        self.api = api
        self.secret = secret
        self.client = UMFutures(key=api, secret=secret)

    def get_balance_usdt(self):
        try:
            response = self.client.balance(recvWindow=10000)
            for elem in response:
                if elem['asset'] == 'USDT':
                    return float(elem['balance'])
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def get_positions(self):
        try:
            resp = self.client.get_position_risk(recvWindow=10000)
            pos = []
            for elem in resp:
                if float(elem['positionAmt']) != 0:
                    pos.append(elem['symbol'])
            return pos
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def check_orders(self):
        try:
            response = self.client.get_orders(recvWindow=10000)
            sym = []
            for elem in response:
                sym.append(elem['symbol'])
            return sym
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def close_open_orders(self, symbol):
        try:
            response = self.client.cancel_open_orders(symbol=symbol, recvWindow=10000)
            print(response)
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def get_tickers_usdt(self):
        try:
            tickers = []
            resp = self.client.ticker_price()
            for elem in resp:
                if 'USDT' in elem['symbol']:
                    tickers.append(elem['symbol'])
            return tickers
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def get_pnl(self, limit):
        try:
            resp = self.client.get_income_history(incomeType="REALIZED_PNL", limit=limit, recvWindow=10000)[::-1]
            pnl = 0
            for elem in resp:
                pnl += float(elem['income'])
            return pnl
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def klines(self, symbol, timeframe):
        try:
            resp = pd.DataFrame(self.client.klines(symbol, timeframe, recvWindow=10000))
            resp = resp.iloc[:, :6]
            resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            resp = resp.set_index('Time')
            resp.index = pd.to_datetime(resp.index, unit='ms')
            resp = resp.astype(float)
            return resp
        except ClientError as error:
            print(
                f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def set_leverage(self, symbol, level):
        try:
            response = self.client.change_leverage(
                symbol=symbol, leverage=level, recvWindow=10000
            )
            print(response)
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def set_mode(self, symbol, type):
        try:
            response = self.client.change_margin_type(
                symbol=symbol, marginType=type, recvWindow=10000
            )
            print(response)
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def get_precisions(self, symbol):
        try:
            resp = self.client.exchange_info()['symbols']
            for elem in resp:
                if elem['symbol'] == symbol:
                    return elem['pricePrecision'], elem['quantityPrecision']
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def get_commission(self, symbol):
        try:
            resp = self.client.commission_rate(symbol=symbol, recvWindow=10000)
            return float(resp['makerCommissionRate']), float(resp['takerCommissionRate'])
        except ClientError as error:
            print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")

    def open_order_market(self, symbol, side, volume, leverage, mode, tp, sl):
        self.set_leverage(symbol, leverage)
        self.set_mode(symbol, mode)
        price = float(self.client.ticker_price(symbol)['price'])
        qty_precision = self.get_precisions(symbol)[1]
        price_precision = self.get_precisions(symbol)[0]
        qty = round(volume / price, qty_precision)
        if side == 'buy':
            try:
                resp1 = self.client.new_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty, recvWindow=10000)
                print(resp1)
                sleep(1)
                sl_price = round(price - price * sl, price_precision)
                resp2 = self.client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, stopPrice=sl_price, closePosition="true", workingType="MARK_PRICE", recvWindow=10000)
                print(resp2)
                sleep(1)
                tp_price = round(price + price * tp, price_precision)
                resp3 = self.client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, stopPrice=tp_price, closePosition="true", workingType="MARK_PRICE", recvWindow=10000)
                print(resp3)
            except ClientError as error:
                print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")
        if side == 'sell':
            try:
                resp1 = self.client.new_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty, recvWindow=10000)
                print(resp1)
                sleep(1)
                sl_price = round(price + price * sl, price_precision)
                resp2 = self.client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, stopPrice=sl_price, closePosition="true", workingType="MARK_PRICE", recvWindow=10000)
                print(resp2)
                sleep(1)
                tp_price = round(price - price * tp, price_precision)
                resp3 = self.client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, stopPrice=tp_price, closePosition="true", workingType="MARK_PRICE", recvWindow=10000)
                print(resp3)
            except ClientError as error:
                print(f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")
