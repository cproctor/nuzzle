from datetime import datetime
import json
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    Boolean,
    Float,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Alarm(Base):
    __tablename__ = 'alarms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime)
    owner = Column(Text)
    creator = Column(Text)
    message_source = Column(Text)

    def __init__(self, params):
        # time may be either a string or a datetime
        if isinstance(params['time'], datetime):
            self.time = params['time']
        elif isinstance(params['time'], basestring):
            self.time = datetime.strptime(params['time'], '%Y-%m-%d %H:%M:%S')

        self.owner = params['owner']
        self.creator = params['creator']
        self.message_source = params['message_source']
        if not (
            isinstance(self.time, datetime) and 
            isinstance(self.owner, basestring) and 
            isinstance(self.creator, basestring) and 
            isinstance(self.message_source, basestring)
        ):
            raise Exception("Invalid alarm")

    def serializable(self):
        return {
            'id': self.id,
            'owner': self.owner,
            'creator': self.creator,
            'message_source': self.message_source,
            'time': str(self.time)
        }

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text)
    name = Column(Text)
    owner = Column(Text)
    in_queue = Column(Boolean)
    queue_weight = Column(Float)
    played = Column(Boolean)
    time_played = Column(DateTime)
    is_default = Column(Boolean)

    def __init__(self, params):
        self.name = params['name']
        self.owner = params['owner']
        self.in_queue = False
        self.played = False
        self.is_default = False

        if not (
            isinstance(self.name, basestring) and
            isinstance(self.owner, basestring)
        ):
            raise Exception("Invalid message")

    def set_queue_position(self, position):
        "Set queue weight so that it is in the nth position when sorted"
            
    def serializable(self):
        return {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'owner': self.owner,
            'in_queue': self.in_queue,
            'queue_weight': self.queue_weight,
            'played': self.played,
            'time_played': self.time_played,
            'is_default': self.is_default
        }
            
