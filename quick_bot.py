import sys
sys.path.insert(0,'..')
from binance_api import BinanceAPI
from credentials import Credentials
import pandas as pd
import time
from twilio_messaging import TwilioMessaging
import logging
import schedule

logging.basicConfig(filename="support_resistance.log", level=logging.INFO, format='%(asctime)s:%(message)s')
logging.getLogger('schedule').propagate = False


class SimpleSupportResistanceBot:
    
    def __init__(self):
        credentials = Credentials()
        self.binance_api = BinanceAPI(credentials.binance_key, credentials.binance_secret)
        self.twilio = TwilioMessaging()
        self.bid = None
        self.ask = None
        self.pair = sys.argv[2]
        self.entry_price = float(sys.argv[3])
        self.exit_price = float(sys.argv[4])
        self.trade_size_usdt = float(sys.argv[6])
        self.trade_size_coin = float(self.binance_api.dollars_to_amount(self.pair, self.trade_size_usdt))
        self.stop_loss = float(sys.argv[5])
        self.in_position = False
        self.shutdown_bot = False


        self.update_order_book()

    def check_for_buy(self):
        if not self.in_position and self.bid < self.entry_price:
            order = self.binance_api.market_buy(self.pair, self.trade_size_coin)
            if order is not None:
                self.trade_size_coin = float(order['executedQty'])
                self.twilio.message(f'Purchased ${self.trade_size_usdt} of {self.pair} @ ${self.bid}')
                logging.info(order)
                self.in_position = True

    def check_for_sell(self):
        if self.in_position and self.bid > self.exit_price:
            order = self.binance_api.market_sell(self.pair, self.trade_size_coin)
            if order is not None:
                pct_return = (self.bid / self.entry_price - 1) * 100
                dollar_return = pct_return * self.trade_size_usdt / 100
                self.twilio.message(f'Sold ${self.trade_size_usdt} of {self.pair} @ ${self.bid}\n'
                                    f'Trade Result: Successful Trade!\n'
                                    f'Return (%) {pct_return:.2f}\n'
                                    f'Return ($) {dollar_return:.2f}')
                self.shutdown_bot = True


        elif self.in_position and self.bid < self.stop_loss:
            order = self.binance_api.market_sell(self.pair, self.trade_size_coin)
            if order is not None:
                pct_return = (self.bid / self.entry_price - 1) * 100
                dollar_return = pct_return * self.trade_size_usdt
                self.twilio.message(f'Sold ${self.trade_size_usdt} of {self.pair} @ ${self.bid}\n'
                                    f'Trade Result: Exited at Loss!\n'
                                    f'Return (%) {pct_return:.2f}\n'
                                    f'Return ($) {dollar_return:.2f}')
                self.shutdown_bot = True



    def update_order_book(self):
        valid, bid_ask = self.binance_api.bid_ask(self.pair)
        if valid:
            self.bid = bid_ask['bid']
            self.ask = bid_ask['ask']

    def run(self):
        schedule.every(5).seconds.do(self.update_order_book)
        schedule.every(5).seconds.do(self.check_for_buy)
        schedule.every(5).seconds.do(self.check_for_sell)

        while not self.shutdown_bot:
            schedule.run_pending()
            time.sleep(4)
        
if __name__ == '__main__':
    s = SimpleSupportResistanceBot()
    s.run()
