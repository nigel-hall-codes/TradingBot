import json


class Credentials:
    
    def __init__(self):

        credentials_path = "/Users/nigel/BotWork/venv/private_keys"
        credentials_file = open(credentials_path).read()
        
        self.credentials = json.loads(credentials_file)
        self.binance_key = self.credentials['binance']['key']
        self.binance_secret = self.credentials['binance']['secret']
        self.twilio_sid = self.credentials['twilio']['sid']
        self.twilio_token = self.credentials['twilio']['token']
