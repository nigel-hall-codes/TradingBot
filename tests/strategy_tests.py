import unittest
import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from strategy import Strategy
from credentials import Credentials
import pandas as pd
import time
import json


class StrategyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        credentials = Credentials()
        cls.binance_api = BinanceAPI(credentials.key, credentials.secret)
        cls.s = Strategy()

    # def test_check_initial_buy_signal(self):
    #     self.strategy.check_initial_buy_signal()

    def test_least_resistance_level(self):
        print(self.s.lower_resistance_level, self.s.upper_resistance_level, self.s.target_gain)
        assert type(self.s.lower_resistance_level) is float and type(self.s.upper_resistance_level) is float
        
    def test_check_first_entry(self):
        print(self.s.lower_resistance_level, self.s.upper_resistance_level, self.s.target_gain)
        print(self.s.df1.iloc[-2:][['Close', "Low"]])
        
        
    
if __name__ == '__main__':
    unittest.main()