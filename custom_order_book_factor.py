import os
import sqlite3
import pandas as pd

class CustomOrderBookFactor:

    def __init__(self, is_local):
        self.is_local = is_local
        self.sqlite_path = '/home/nhall/BOTvenv2/bots/SupplyDemandRatioETHUSDT.db'
        self.remote_path = '/Users/nigel/BotWork/venv/SupplyDemandRatioETHUSDT.db'
        
    


