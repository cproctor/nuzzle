from pyramid.response import Response
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Alarm,
    Message, 
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

@view_config(route_name='get_next_message', renderer='json')
def get_next_message(request):
    owner = request.matchdict['user']
    query = DBSession.query(Message).filter(Message.owner == owner).filter(Message.in_queue == True).order_by(Message.queue_weight)
    nextMessage = query.first()
    if nextMessage:
        return nextMessage.serializable()
    else:
        query = DBSession.query(Message).filter(Message.is_default == True)
        default = query.first()
        if default:
            return default.serializable()
        else:
            request.response.status = 400
            return {'status': 'error', 'error': 'no next message'}

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

@view_config(route_name='set_queue_position', renderer='json')
def set_queue_position(request):
    #try:
    if True:
        message = _get_message(request)
        position = int(request.matchdict['position'])
        query = DBSession.query(Message).filter(Message.owner == request.matchdict['user']).filter(Message.in_queue == True).order_by(Message.queue_weight)
        queue = query.all()
        queueLength = query.count()
        if queueLength == 0: 
            message.queue_weight = 0
        elif position == 0: # We want the beginning of the queue
            message.queue_weight = queue[0].queue_weight - 1
        elif position >= queueLength: # We want the end of the queue
            message.queue_weight = query[queueLength - 1].queue_weight + 1
        else: # We want the middle of the queue
            neighbors = query[position:position + 2]
            message.queue_weight = (neighbors[0].queue_weight + neighbors[1].queue_weight) / 2
        message.in_queue = True
        DBSession.flush()
        queue = query.all()
        return message.serializable()
    #except Exception, e: 
        #return _error(request, repr(e))

@view_config(route_name='remove_from_queue', renderer='json')
def remove_from_queue(request):
    try:
        message = _get_message(request)
        message.in_queue = False
        DBSession.flush()
        return message.serializable()
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='mark_as_played', renderer='json')
def mark_as_played(request):
    try:
        message = _get_message(request)
        message.played = True
        DBSession.flush()
        return message.serializable()
    except Exception, e: 
        return _error(request, repr(e))

@view_config(route_name='mark_as_unplayed', renderer='json')
def mark_as_unplayed(request):
    try:
        message = _get_message(request)
        message.played = False
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
    owner = request.matchdict['user']
    id = request.matchdict['messageId']
    query = DBSession.query(Message).filter(Message.owner == owner).filter(Message.id == id)
    return query.one()

def _error(request, message=""):
    request.response = 400
    return {
        'status': 'error',
        'error': message
    }
