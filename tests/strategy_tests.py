import unittest
import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from strategy import Strategy
from credentials import Credentials
import pandas as pd
import time
import json
import datetime


class StrategyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        credentials = Credentials()
        cls.binance_api = BinanceAPI(credentials.binance_key, credentials.binance_secret)
        cls.s = Strategy()
        cls.s.max_per_trade = 100

    def test_positive_first_entry_signal(self):

        self.s.locked_resistance_levels = True
        self.s.previous_minute_low = self.s.ask - 1
        self.s.current_close = self.s.ask + 1
        self.s.first_entry_price = self.s.ask
        self.s.check_for_first_entry()

        assert 0 in self.s.current_entries

        self.binance_api.market_sell("ETHUSDT", float(self.s.last_order['executedQty']))

    def test_positive_second_entry_signal(self):

        self.s.locked_resistance_levels = True
        self.s.second_entry_price = self.s.ask
        self.s.previous_minute_low = self.s.second_entry_price - 1
        self.s.current_close = self.s.second_entry_price + 1
        self.s.current_entries[0] = {"entry": {"price": self.s.ask - 10,
                                               "dt": datetime.datetime.now(),
                                               "quantity": .2}}

        self.s.check_for_second_entry()

        assert 1 in self.s.current_entries

        self.binance_api.market_sell("ETHUSDT", float(self.s.current_entries[1]['entry']['quantity']))

    def test_positive_third_entry(self):
                
        self.s.locked_resistance_levels = True
        self.s.third_entry_price = self.s.ask
        self.s.previous_minute_low = self.s.third_entry_price - 1
        self.s.current_close = self.s.third_entry_price + 1
        self.s.current_entries[0] = {"entry": {"price": self.s.ask - 10,
                                               "dt": datetime.datetime.now(),
                                               "quantity": .2}}
        self.s.current_entries[1] = {"entry": {"price": self.s.ask - 5,
                                               "dt": datetime.datetime.now(),
                                               "quantity": .2}}

        self.s.check_for_third_entry()

        assert 2 in self.s.current_entries

        self.binance_api.market_sell("ETHUSDT", float(self.s.current_entries[2]['entry']['quantity']))

    def test_exit_entire_trade(self):
        
        max_per_trade = .75
        self.binance_api.market_buy("ETHUSDT", max_per_trade)
        
        for i in range(0,3):
            self.s.current_entries[i] = {"entry": {"price": self.s.ask - 5,
                                               "dt": datetime.datetime.now(),
                                               "quantity": (max_per_trade / 3)}}
            
        self.s.exit_entire_trade()
        print(self.s.last_order['executedQty'])
        assert float(self.s.last_order['executedQty']) == max_per_trade
        

    def test_least_resistance_level(self):
        # print(self.s.lower_resistance_level, self.s.upper_resistance_level, self.s.target_gain)
        assert type(self.s.lower_resistance_level) is float and type(self.s.upper_resistance_level) is float
        

    
    
if __name__ == '__main__':
    unittest.main()
    
    
