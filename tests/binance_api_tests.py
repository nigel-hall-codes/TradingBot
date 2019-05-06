import unittest
import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from credentials import Credentials
import pandas as pd
import time


class BinanceAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        credentials = Credentials()
        cls.binance_api = BinanceAPI(credentials.key, credentials.secret)

    def test_market_buy(self):
        
        pair = 'XRPUSDT'
        amount_to_test = self.binance_api.dollars_to_amount(pair, 40)

        self.binance_api.market_buy(pair, amount_to_test)
        last_trade = self.binance_api.last_trade(pair)
        time.sleep(2)
        time_since_last_trade = self.binance_api.get_server_time() - last_trade['time']
        assert time_since_last_trade < pd.Timedelta(minutes=1)

        self.binance_api.market_sell(pair, amount_to_test)

    def test_market_sell(self):

        pair = "XRPUSDT"
        amount_to_test = self.binance_api.dollars_to_amount(pair, 40)

        self.binance_api.market_buy(pair, amount_to_test)
        time.sleep(3)
        self.binance_api.market_sell(pair, amount_to_test)
        time.sleep(3)

        last_trade = self.binance_api.last_trade(pair)
        time_since_last_trade = self.binance_api.get_server_time() - last_trade['time']

        assert time_since_last_trade < pd.Timedelta(minutes=1) and not last_trade['isBuyer']
        
    def test_dollar_to_amount(self):
        assert type(self.binance_api.dollars_to_amount("XRPUSDT", 50)) is float
        
    def test_bid_ask(self):
        bid_ask = self.binance_api.bid_ask("BTCUSDT")
        assert type(bid_ask['bid']) is float and type(bid_ask['ask']) is float

    def test_1m_data(self):
        df = self.binance_api.historical_data_1m("BTCUSDT", 540)
        assert df.shape[0] == 540
        
        
        

if __name__ == '__main__':
    unittest.main()



