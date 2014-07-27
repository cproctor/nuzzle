from datetime import datetime
from pyramid.response import Response
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Alarm,
    Message, 
    MessagePlay,
    MessageQueuePosition,
    )

@view_config(route_name='get_alarms', renderer='json')
def get_alarms(request):
    alarms = DBSession.query(Alarm).all()
    return [a.serializable() for a in alarms]

@view_config(route_name='create_alarm', renderer='json')
def create_alarm(request):
    try:
        params = request.json_body
        params['owner'] = request.matchdict['user']
        alarm = Alarm(params)
        DBSession.add(alarm)
        DBSession.flush()
    except Exception, e:
        request.response.status = 400
        return "ERROR: %s" % e
    return alarm.serializable()
    
@view_config(route_name='cancel_alarm', renderer='json')
def cancel_alarm(request):
    try:
        owner = request.matchdict['user']
        id = request.matchdict['alarmId']
        alarm = DBSession.query(Alarm).filter(Alarm.owner == owner).filter(Alarm.id == id).first()
        DBSession.delete(alarm)
    except Exception, e:
        request.response.status = 400
        return "ERROR: %s" % e
    return {"status": "OK"}

# MESSAGES
# ========

@view_config(route_name='get_messages', renderer='json')
def get_messages(request):
    messages = DBSession.query(Message).all()
    return [m.serializable() for m in messages]

@view_config(route_name='get_message', renderer='json')
def get_message(request):
    mId = request.matchdict['messageId']
    owner = request.matchdict['user']
    message = DBSession.query(Message).filter(Message.owner == owner).filter(Message.id == mId).one()
    return message.serializable()

@view_config(route_name='create_message', renderer='json')
def create_message(request):
    try:
        params = request.json_body
        params['owner'] = request.matchdict['user']
        message = Message(params)
        DBSession.add(message)
        DBSession.flush()
        return message.serializable()
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='delete_message', renderer='json')
def delete_message(request):
    try: 
        message = _get_message(request)
        DBSession.delete(message)
        return {'status': 'OK'}
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='get_queue', renderer='json')
def get_queue(request):
    try:
        return [m.serializable() for m in _get_queued_messages(request)]
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='get_next_message', renderer='json')
def get_next_message(request):
    try: 
        messages = _get_queued_messages(request)
        if any(messages):
            return messages[0].serializable()
        else:
            return _error(request, 'No messages in queue')
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='append_to_queue', renderer='json')
def append_to_queue(request):
    try:
        message = _get_message_by_owner_and_id(request.matchdict['user'], 
                request.json_body['id'])
        position = _get_queue_length(request)
        message.positions.append(MessageQueuePosition(user=message.owner, position=position))
        DBSession.flush()
        return [m.serializable() for m in _get_queued_messages(request)]
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='add_to_queue', renderer='json')
def add_to_queue(request):
    #try:
    if True:
        message = _get_message_by_owner_and_id(request.matchdict['user'], 
                request.json_body['id'])
        position = max(0, min(int(request.matchdict['position']), _get_queue_length(request)))
        message.positions.append(MessageQueuePosition(user=message.owner, position=position))
        _increment_queue_positions(request, position)
        DBSession.flush()
        return [m.serializable() for m in _get_queued_messages(request)]
    #except Exception, e: 
        #return _error(request, repr(e))

@view_config(route_name='remove_from_queue', renderer='json')
def remove_from_queue(request):
    try:
        position = int(request.matchdict['position'])
        DBSession.delete(_get_queue(request)[position])
        DBSession.flush()
        return [m.serializable() for m in _get_queued_messages(request)]
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='mark_as_played', renderer='json')
def mark_as_played(request):
    try:
        message = _get_message(request)
        playtime = datetime.strptime(request.json_body['time_played'], 
                '%Y-%m-%d %H:%M:%S')
        message.plays.append(MessagePlay(time_played=playtime))
        DBSession.flush()
        return message.serializable()
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='mark_as_unplayed', renderer='json')
def mark_as_unplayed(request):
    try:
        message = _get_message(request)
        for play in message.plays: 
            DBSession.delete(play)
        DBSession.flush()
        return message.serializable()
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='set_as_default', renderer='json')
def set_as_default(request):
    try:
        message = _get_message(request)
        message.is_default = True
        defaults = DBSession.query(Message).filter(Message.is_default == True).all()
        for defaultMessage in defaults: 
            if defaultMessage is not message:
                defaultMessage.is_default = False    
        DBSession.flush()
        return message.serializable()
    except Exception, e: 
        return _error(request, repr(e))

def _get_message(request):
    return _get_message_by_owner_and_id(request.matchdict['user'], 
            request.matchdict['messageId'])

def _get_message_by_owner_and_id(owner, mId):
    return DBSession.query(Message).filter(Message.owner == owner).filter(Message.id == mId).one()

def _get_queue(request):
    owner = request.matchdict['user']
    return DBSession.query(MessageQueuePosition).filter(MessageQueuePosition.user == owner).order_by(MessageQueuePosition.position).all()

def _get_queued_messages(request):
    owner = request.matchdict['user']
    return [_get_message_by_owner_and_id(owner, q.message_id) 
            for q in _get_queue(request)]

def _increment_queue_positions(request, insertionPoint):
    queue = _get_queue(request)
    for queuedItem in queue[insertionPoint:]:
        queuedItem.position += 1

def _get_queue_length(request):
    owner = request.matchdict['user']
    query = DBSession.query(MessageQueuePosition).filter(MessageQueuePosition.user == owner).order_by(MessageQueuePosition.position)
    return query.count()

def _error(request, message=""):
    request.response.status = 400
    return {
        'status': 'error',
        'error': message
    }
