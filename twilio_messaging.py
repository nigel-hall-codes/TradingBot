from twilio.rest import Client
import datetime
from credentials import Credentials

class TwilioMessaging:

    def __init__(self):
        credentials = Credentials()
        self.client = Client(credentials.twilio_sid, credentials.twilio_token)
        self.twilio_number = '+13203350611'
        self.to_numbers = ['+14156723287']

    def message(self, msg):
        for number in self.to_numbers:
            message = self.client.messages.create(to=number, from_=self.twilio_number, body=msg)
            return message
        
        