import unittest
import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from quick_bot import SimpleSupportResistanceBot
from credentials import Credentials
import pandas as pd
import time
import json
import datetime


class QuickBotTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        credentials = Credentials()
        cls.binance_api = BinanceAPI(credentials.binance_key, credentials.binance_secret)
        cls.s = SimpleSupportResistanceBot()


    def test_check_for_buy_and_sell(self):
        self.s.bid = self.s.entry_price - 1
        self.s.check_for_buy()
        self.s.bid = self.s.exit_price + 1
        self.s.check_for_sell()






if __name__ == '__main__':
    unittest.main()
    
    
