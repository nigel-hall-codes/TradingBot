import unittest
import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from strategy import Strategy
from credentials import Credentials
from twilio_messaging import TwilioMessaging
import pandas as pd
import time
import json


class TwilioMessagingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.messenger = TwilioMessaging()

    def test_messenger(self):
        message = self.messenger.message("I like your security jacket")
        assert message.error_code is None

if __name__ == '__main__':
    unittest.main()