from peewee import *
import subprocess
import os
import time
import models
from models import Bot, BotSettings


class Manager:

    def __init__(self):
        # self.bots_path = "/home/nhall/BOTvenv2/bots/"
        self.bots_path = "/Users/nigel/BotWork/venv/RSI-MACD-BOT/TradingBot"

    def set_allocation(self, bot_name, dollar_amount):
        b_id = Bot.get(name=bot_name).id
        settings = BotSettings.get(id=b_id)
        settings.allocation = dollar_amount
        settings.save()
        print("Allocation set to {}".format(settings.allocation))

    def start_bot(self, b, allocation):

        b = Bot.get_or_create(name=b)[0]
        command = "nohup python3 {}.py".format(self.bots_path + b.name)
        settings, created = BotSettings.get_or_create(id=b.id)
        p = subprocess.Popen(command.split(" "), stdout=open(self.bots_path + b.name + ".out", 'w'),
             stderr=open('{}.log'.format(self.bots_path + b.name), 'w+'),
             preexec_fn=os.setpgrp)

        settings.pid = p.pid
        settings.allocation = allocation
        settings.bot_live = True
        settings.save()

        print("Started Bot: {} PID: {} with allocation of ${}".format(b.name, p.pid,  allocation))

    def fetch_live_bots(self):
        bots = BotSettings.select().where(BotSettings.bot_live)
        return [bot for bot in bots]

    def shutdown_bot(self, name):
        b = Bot.get(name=name)
        settings = BotSettings.get(id=b.id)
        subprocess.Popen(["kill", "-9", str(settings.pid)])
        settings.bot_live = False
        settings.save()
        print("Killed bot: {}".format(name))

    def shutdown_all_bots(self):
        live_bots = BotSettings.select().where(BotSettings.bot_live == True)
        for bot in live_bots:
            name = Bot.get(id=bot.id).name
            self.shutdown_bot(name)
            print("Killed bot {}".format(name))

    def shutdown_and_redeploy(self):
        live_bots = self.fetch_live_bots()
        for bot in live_bots:
            allocation = bot.allocation
            name = Bot.get(id=bot.id).name
            self.shutdown_bot(name)
            self.start_bot(name, allocation)





