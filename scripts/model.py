
import datetime

from peewee import SqliteDatabase, Model, Proxy, CharField, BooleanField, \
     DateTimeField, IntegerField, ForeignKeyField, FloatField


proxy = Proxy()

class Database:
    def __init__(self, filename):
        self.db = SqliteDatabase(filename)
        self.db.connect()
        proxy.initialize(self.db)
        self.db.create_tables([Group, Event, EventTime])

class Group(Model):
    id = CharField(primary_key=True)
    fetched_events = BooleanField(default=False)
    last_fetched = DateTimeField(default=datetime.datetime.fromtimestamp(0))
    class Meta:
        database = proxy


class Event(Model):
    id = CharField(primary_key=True)
    name = CharField(default="")
    location = CharField(default="")
    image = CharField(default="")
    recurring = IntegerField(default=-1)
    fetched_times = BooleanField(default=False)
    last_fetched = DateTimeField(default=datetime.datetime.fromtimestamp(0))
    class Meta:
        database = proxy


class EventTime(Model):
    event = ForeignKeyField(Event)
    time_str = CharField()
    time_from = DateTimeField()
    time_delta = FloatField()
    class Meta:
        database = proxy
