import unittest
import transaction
import json
from pyramid import testing
from pyramid.paster import get_app
from .models import DBSession
from datetime import datetime
from unittest import skip

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class FunctionalTests(unittest.TestCase):

    def setUp(self):
        from webtest import TestApp
        app = get_app('testing.ini#main')
        self.testapp = TestApp(app)

    def tearDown(self):
        self.delete_alarms('ed')
        self.delete_messages('ed')

    def create_alarm(self, owner, creator):
        params = {
            'time': now(),
            'creator': creator,
            'message_source': creator,
        }
        res = self.testapp.post_json('/api/v1/alarms/%s' % owner, params)
        return res.json

    def delete_alarm(self, owner, id):
        self.testapp.delete('/api/v1/alarms/%s/%s' % (owner, id))

    def get_alarms(self, owner):
        res = self.testapp.get('/api/v1/alarms/%s' % owner)
        return res.json

    def delete_alarms(self, owner):
        for alarm in self.get_alarms(owner):
            self.delete_alarm(owner, alarm['id'])

    def create_message(self, owner, name):
        params = {
            'owner': owner,
            'name': name
        }
        res = self.testapp.post_json('/api/v1/messages/%s' % owner, params)
        return res.json

    def delete_message(self, owner, id):
        url = '/api/v1/messages/%s/%s' % (owner, id)
        res = self.testapp.delete(url)
        
    def get_messages(self, owner):
        res = self.testapp.get('/api/v1/messages/%s' % owner)
        return res.json

    def get_message(self, owner, messageId):
        res = self.testapp.get('/api/v1/messages/%s/%s' % (owner, messageId))
        return res.json

    def delete_messages(self, owner):
        for message in self.get_messages(owner):
            self.delete_message(owner, message['id'])

    def add_to_queue(self, owner, messageId, position):
        params = (owner, messageId, position)
        self.testapp.put('/api/v1/messages/%s/%s/queue/position/%s' % params)

    def test_get_alarms(self):
        for i in range(3):
            self.create_alarm('ed', 'person%s' % i)
        res = self.testapp.get('/api/v1/alarms/ed', status=200)
        self.failUnless(len(res.json) is 3)

    def test_create_alarm(self):
        self.create_alarm('ed', 'creator')
        self.failUnless(len(self.get_alarms('ed')) == 1)

    def test_cancel_alarm(self):
        self.create_alarm('ed', 'person')
        alarm = self.get_alarms('ed')[0]
        self.delete_alarm('ed', alarm['id'])
        self.failUnless(not any(self.get_alarms('ed')))

    def test_get_messages(self):
        self.create_message('ed', 'm1')
        self.failUnless(len(self.get_messages('ed')) == 1)

    def test_get_next_message_when_no_message_in_queue(self):
        try:
            res = self.testapp.get('/api/v1/messages/ed/next')
            error = False
        except:
            error = True
        self.failUnless(error)

    def test_get_next_message_when_default(self):
        m = self.create_message('ed', 'm1')
        self.testapp.put('/api/v1/messages/ed/%s/default' % m['id'])
        res = self.testapp.get('/api/v1/messages/ed/next')
        self.failUnless(m['id'] == res.json['id'])

    def test_create_message(self):
        self.create_message('ed', 'm1')
        self.failUnless(len(self.get_messages('ed')) == 1)

    def test_delete_message(self):
        m1 = self.create_message('ed', 'm1')
        m2 = self.create_message('ed', 'm2')
        self.delete_message('ed', m1['id'])
        self.failUnless(len(self.get_messages('ed')) == 1)

    def test_set_queue_position(self):
        m = [self.create_message('ed', 'm%s' % i) for i in range(3)]
        for msg in m:
            self.add_to_queue('ed', msg['id'], 0)
        nextMsg = self.testapp.get('/api/v1/messages/ed/next').json
        self.failUnless(nextMsg['id'] == 3)

    def test_remove_from_queue(self):
        m = [self.create_message('ed', 'm%s' % i) for i in range(3)]
        for msg in m:
            self.add_to_queue('ed', msg['id'], 0)
        self.testapp.put('/api/v1/messages/ed/3/queue/remove')
        nextMsg = self.testapp.get('/api/v1/messages/ed/next').json
        self.failUnless(nextMsg['id'] == 2)
        self.testapp.put('/api/v1/messages/ed/2/queue/remove')
        nextMsg = self.testapp.get('/api/v1/messages/ed/next').json
        self.failUnless(nextMsg['id'] == 1)

    def test_mark_as_played(self):
        m1 = self.create_message('ed', 'm1')
        self.failUnless(not m1['played'])
        self.testapp.put('/api/v1/messages/ed/1/played')
        m1 = self.get_message('ed', m1['id'])
        self.failUnless(m1['played'])

    def test_mark_as_unplayed(self):
        m = self.create_message('ed', 'm1')
        messages = self.get_messages('ed')
        self.failUnless(not messages[0]['played'])
        self.testapp.put('/api/v1/messages/ed/%s/played' % m['id'])
        messages = self.get_messages('ed')
        self.failUnless(messages[0]['played'])
        self.testapp.put('/api/v1/messages/ed/%s/unplayed' % m['id'])
        messages = self.get_messages('ed')
        self.failUnless(not messages[0]['played'])

    def test_set_as_default(self):
        m = self.create_message('ed', 'm1')
        messages = self.get_messages('ed')
        self.failUnless(not messages[0]['is_default'])
        self.testapp.put('/api/v1/messages/ed/%s/default' % m['id'])
        messages = self.get_messages('ed')
        self.failUnless(messages[0]['is_default'])

