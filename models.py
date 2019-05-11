from peewee import *


db = SqliteDatabase("tradesv2.db")
settingsDB = SqliteDatabase("BotSettingsv2.db")


class Trade(Model):

    bot_name = TextField()
    quantity = FloatField()
    first_trade_time = DateTimeField()
    entry_price = FloatField()
    exit_price = FloatField()
    entry_time = DateTimeField()
    exit_time = DateTimeField()
    target_entry = FloatField()
    target_exit_entry = FloatField()
    entry_level = IntegerField()
    
    class Meta:
        database = db


class Bot(Model):

    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = settingsDB


class BotSettings(Model):

    id = IntegerField()
    pid = IntegerField(default=0)
    bot_live = BooleanField(default=False)
    allocation = FloatField(default=0)

    class Meta:
        database = settingsDB


def initialize():
    db.connect()
    db.create_tables([Trade])
    settingsDB.connect()
    settingsDB.create_tables([Bot, BotSettings])
    
    
initialize()
