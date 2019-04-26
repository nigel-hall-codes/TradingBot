import unittest
import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from credentials import Credentials
from custom_order_book_factor import CustomOrderBookFactor
import pandas as pd
import time

class CustomOrderBookFactorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        credentials = Credentials()
        cls.binance_api = BinanceAPI(credentials.key, credentials.secret)
        cls.custom_order_book_factor = CustomOrderBookFactor(is_local=False)

    def test_order_book_data(self):
        print(self.custom_order_book_factor.data())


if __name__ == '__main__':
    unittest.main()



