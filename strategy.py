import binance_api
from credentials import Credentials
from sklearn.preprocessing import scale
import datetime
import pandas as pd
import schedule
import logging
from twilio_messaging import TwilioMessaging
from models import Trade
import os
import models

logging.basicConfig(filename="strategy.log", level=logging.INFO, format='%(asctime)s:%(message)s')
logging.getLogger('schedule').propagate = False


class Strategy:

    def __init__(self):
        
        self.credentials = Credentials()
        self.binance_api = binance_api.BinanceAPI(self.credentials.binance_key, self.credentials.binance_secret)
        self.twilio = TwilioMessaging()
        self.current_entries = {}
        self.last_order = None
        self.lower_resistance_level = None
        self.upper_resistance_level = None
        self.target_gain = None
        self.first_entry_price = None
        self.second_entry_price = None
        self.third_entry_price = None

        self.bid = None
        self.ask = None
        self.previous_minute_low = None
        self.current_close = None
        self.locked_resistance_levels = False
        self.df1 = None

        self.pair = "ETHUSDT"
        self.max_per_trade = 100
        self.trade_size_scale = [.2, .6, .2]
        self.entry_point_scale = [0, .25, .6]

        self.update_order_book()
        self.update_historical_data()
        self.update_least_resistance_levels()

        self.name = os.path.basename(__file__)[:-3]
        # self.bot_id = models.Bot.get(name=self.name).id
        # self.settings = models.BotSettings.get(id=self.bot_id)
        # self.max_per_trade = self.settings.allocation
        self.trade_id = None
        
    def update_least_resistance_levels(self):
        
        df1 = self.df1
        df1['vol ob score'] = scale(df1['Volume'])
        df2 = df1[df1.index > datetime.datetime.now() - datetime.timedelta(hours=8)]
        level_bins = pd.qcut(df2['Close'].sort_values(), 4, duplicates='drop')
        grouped_levels = df2.groupby(level_bins)['vol ob score'].mean().sort_values(ascending=False).reset_index().sort_index()
        grouped_levels['R-Level'] = pd.Series(pd.IntervalIndex(grouped_levels['Close']).right)
        grouped_levels['S-Level'] = pd.Series(pd.IntervalIndex(grouped_levels['Close']).left)
        least_resistance = grouped_levels[grouped_levels['vol ob score'] == grouped_levels['vol ob score'].min()]
        
        self.lower_resistance_level = float(least_resistance['S-Level'].values[0])
        self.upper_resistance_level = float(least_resistance['R-Level'].values[0])
        self.target_gain = self.upper_resistance_level / self.lower_resistance_level - 1
        self.first_entry_price = self.lower_resistance_level
        self.second_entry_price = self.lower_resistance_level * (1 + (self.target_gain * self.entry_point_scale[1]))
        self.third_entry_price = self.lower_resistance_level * (1 + (self.target_gain * self.entry_point_scale[2]))                                                  
        logging.info("Lower: {} Upper: {} Target Gain: {}".format(self.lower_resistance_level,
                                                                  self.upper_resistance_level,
                                                                  self.target_gain))
        
    def check_resistance_level_lock_status(self):
        
        if self.upper_resistance_level / self.lower_resistance_level - 1 > 0.006:
            self.locked_resistance_levels = True
            
        if self.lower_resistance_level / self.ask - 1 > 0.003 or self.ask / self.upper_resistance_level - 1 > 0.003:
            self.locked_resistance_levels = False
        
    def check_for_first_entry(self):
        
        if self.locked_resistance_levels and self.current_entries == {}:
            
            if self.previous_minute_low < self.first_entry_price < self.current_close:
                quantity = self.binance_api.dollars_to_amount(self.pair, self.max_per_trade * self.trade_size_scale[0])
                self.last_order = self.binance_api.market_buy(self.pair, quantity)
                logging.info("Market Buy: {}".format(quantity))
                self.twilio.message("First entry buy: {}\n"
                                    "Lower: {}\n"
                                    "Upper: {}\n"
                                    "Target gain: {}".format(quantity,
                                                             self.lower_resistance_level,
                                                             self.upper_resistance_level,
                                                             self.target_gain))

                self.current_entries[0] = {"entry": {"price": self.ask,
                                                     "dt": datetime.datetime.now(),
                                                     "quantity": quantity}}
            
    def check_for_second_entry(self):
        
        if self.locked_resistance_levels and 0 in self.current_entries:
            
            if self.previous_minute_low < self.second_entry_price < self.current_close:
                quantity = self.binance_api.dollars_to_amount(self.pair, self.max_per_trade * self.trade_size_scale[1])
                self.binance_api.market_buy(self.pair, quantity)
                logging.info("Market Buy: {}".format(quantity))
                self.twilio.message("Second entry buy: {}\n"
                                    "Lower: {}\n"
                                    "Upper: {}\n"
                                    "Target gain: {}".format(quantity,
                                                             self.lower_resistance_level,
                                                             self.upper_resistance_level,
                                                             self.target_gain))

                self.current_entries[1] = {"entry": {"price": self.ask,
                                                     "dt": datetime.datetime.now(),
                                                     "quantity": quantity}}
                
    def check_for_third_entry(self):

        if self.locked_resistance_levels and 1 in self.current_entries:
            
            if self.previous_minute_low < self.third_entry_price < self.current_close:
                quantity = self.binance_api.dollars_to_amount(self.pair, self.max_per_trade * self.trade_size_scale[2])
                self.binance_api.market_buy(self.pair, quantity)
                logging.info("Market Buy: {}".format(quantity))
                self.twilio.message("Third entry buy: {}\n"
                                    "Lower: {}\n"
                                    "Upper: {}\n"
                                    "Target gain: {}".format(quantity,
                                                             self.lower_resistance_level,
                                                             self.upper_resistance_level,
                                                             self.target_gain))

                self.current_entries[2] = {"entry": {"price": self.ask,
                                                     "dt": datetime.datetime.now(),
                                                     "quantity": quantity}}

    def exit_entire_trade(self):
        
        quantity_to_sell = 0
        
        for entry in self.current_entries:
            if "exit" not in self.current_entries[entry]:
                quantity_to_sell += self.current_entries[entry]['entry']['quantity']
                self.current_entries[entry]['exit'] = {"price": self.bid, 
                                                       "quantity": self.current_entries[entry]['entry']['quantity'],
                                                       "dt": datetime.datetime.now()
                                                       }
                
                trade = Trade.create(bot_name=self.name,
                                     quantity=self.current_entries[entry]['entry']['quantity'],
                                     first_trade_time=self.current_entries[0]['entry']['dt'],
                                     entry_time=self.current_entries[entry]['entry']['dt'],
                                     exit_time=self.current_entries[entry]['exit']['dt'],
                                     entry_price=self.current_entries[entry]['exit']['price'],
                                     exit_price=self.current_entries[entry]['exit']['price']
                             )

        self.twilio.message("Entered @ {}\nExited @ {}".format(self.current_entries[0]['entry']['price'], self.bid))
        self.current_entries = {}
        self.last_order = self.binance_api.market_sell(self.pair, quantity_to_sell)
        
        
    def check_stops(self):
        
        if len(self.current_entries) == 1 and self.current_entries[0]['entry']['price'] / self.bid - 1 > 0.003:
            self.exit_entire_trade()

        elif len(self.current_entries) == 2 and self.bid < self.current_entries[0]['entry']['price']:
            self.exit_entire_trade()

        elif len(self.current_entries) == 3 and self.bid < self.current_entries[1]['entry']['price']:
            self.exit_entire_trade()
            
        elif len(self.current_entries) == 3 and self.bid > self.upper_resistance_level:
            self.exit_entire_trade()

    def update_order_book(self):
        
        valid, quote = self.binance_api.bid_ask(self.pair)
        
        if valid:
            self.bid = quote['bid']
            self.ask = quote['ask']
            logging.info("Bid: {} Ask: {}".format(self.bid, self.ask))
        
    def update_historical_data(self):
        
        valid, df = self.binance_api.historical_data_1m(self.pair, 540)
        
        if valid:
            self.df1 = df
            self.previous_minute_low = self.df1['Low'].iloc[-2]
            self.current_close = self.df1['Close'].iloc[-1]

    def run(self):

        schedule.every(5).seconds.do(self.check_for_first_entry)
        schedule.every(5).seconds.do(self.check_for_second_entry)
        schedule.every(5).seconds.do(self.check_for_third_entry)
        schedule.every(10).seconds.do(self.update_historical_data)
        schedule.every(10).seconds.do(self.update_least_resistance_levels)
        schedule.every(10).seconds.do(self.check_resistance_level_lock_status)
        schedule.every(2).seconds.do(self.update_order_book)
        schedule.every(2).seconds.do(self.check_stops)

        while True:
            schedule.run_pending()


if __name__ == '__main__':
    strategy = Strategy()
    strategy.run()
        
        
        
        
