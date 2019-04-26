import os
import sqlite3
import pandas as pd

class CustomOrderBookFactor:

    def __init__(self, is_local):
        self.is_local = is_local
        self.sqlite_path = '/home/nhall/BOTvenv2/bots/SupplyDemandRatioETHUSDT.db'
        self.remote_path = '/Users/nigel/BotWork/venv/SupplyDemandRatioETHUSDT.db'
        
    def download_db_file(self):
     
        child = pexpect.spawn("scp nhall@69.48.212.237:{} {}".format(file_to_download, download_location))
        i = child.expect(["password: ", pexpect.EOF])
        if i == 0:  # send password
            child.sendline("N!g3Lh@ll")
            child.expect(pexpect.EOF)
        elif i == 1:
            print("Got the key or connection timeout")
         
    def data(self):
        
        if self.is_local:
            path = self.sqlite_path
        else:
            path = self.remote_path
        
        try:
            conn = sqlite3.connect(path)
            q = "select * from SupplyDemandRatio order by dt desc limit 6000"
            df = pd.read_sql(q, conn)
            df['dt'] = pd.to_datetime(df['dt'], unit='ms')
            df = df.set_index('dt')
            df = df[df.index > '2019-04-10 18:01:00'].resample('1T').mean().dropna()
            
            return df
        
        except Exception as e:
            print(e)
            



