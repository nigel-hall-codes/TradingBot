from binance.client import Client
import pandas as pd
import talib
import datetime
import numpy as np
import os
import traceback


class BinanceAPI:
    
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.client = Client(self.key, self.secret)
        
    def usdt_balance(self):
        try:
            usdt_balance = float(self.client.get_asset_balance("USDT")['free'])   
        except:
            usdt_balance = None
            
        return usdt_balance
    
    def get_lot_size(self, symbol):
        try:
            for filt in self.client.get_symbol_info(symbol)['filters']:
                if filt['filterType'] == 'LOT_SIZE':
                    return filt['stepSize'].find('1') - 2
        except Exception as e:
            print(e)

    def market_buy(self, pair, amount):
        
        lot_size = self.get_lot_size(pair)
        amount = round(amount, lot_size + 1)

        try:
            order = self.client.create_order(
                symbol=pair,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=amount
            )
            
            return order
        except Exception as e:
            print(e)
            return None
        
    def dollars_to_amount(self, pair, dollars):
        try:
            ticker = self.client.get_ticker(symbol=pair)
            return dollars / float(ticker['lastPrice'])
        
        except Exception as e:
            print(e)
            return None
            
    def get_server_time(self):
        return pd.to_datetime(self.client.get_server_time()['serverTime'], unit='ms')
        
    def market_sell(self, pair, amount):

        lot_size = self.get_lot_size(pair)
        amount = round(amount, lot_size + 1)

        try:
            order = self.client.create_order(
                symbol=pair,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=amount
            )
            
            return order

        except Exception as e:
            print(e)
            return None

    def get_trades(self, pair):
        try:
            trades = pd.DataFrame(self.client.get_my_trades(symbol=pair))
            trades['time'] = pd.to_datetime(trades['time'], unit='ms')
            return trades
        except:
            return None
    
    def last_trade(self, pair):
        return self.get_trades(pair).iloc[-1]
    
    def bid_ask(self, pair):
        try:
            ticker = self.client.get_ticker(symbol=pair)
            return True, {"bid": float(ticker['bidPrice']), "ask": float(ticker['askPrice'])}
        except Exception as e:
            print(e)
            return False, {"bid": None, "ask": None}

    def historical_data_1m(self, pair, n):
        try:
            data = self.client.get_historical_klines(pair,
                                                     Client.KLINE_INTERVAL_1MINUTE,
                                                     "%s minutes ago UTC" % str(n))
            df = pd.DataFrame(data)
    
            df.columns = ['OTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CTime', 'Quote Asset Volume',
                          '# of Trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'ignored']
            df['Close'] = df['Close'].astype(float)
            df['Volume'] = df['Volume'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['pair'] = pair
            df['CTime'] = pd.to_datetime(df['CTime'], unit='ms')
            df = df.set_index('CTime')
            assert df.shape[0] >= (n - 1)
            return True, df
        
        except Exception as e:
            print(e)
            return False, None
        
    def orders(self, pair):
        try:
            orders = pd.DataFrame(self.client.get_all_orders(symbol=pair))
            return orders
        
        except:
            return None
            
        


        
        
            
                                                     
        
        
    
    

    

    
    
    
        
    
        
    
        
    


