from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include(api_routes, route_prefix='/api/v1')

    config.add_route('home', '/')

    config.scan()
    return config.make_wsgi_app()

def api_routes(config):
    config.include(api_alarm_routes, route_prefix='/alarms')
    config.include(api_message_routes, route_prefix='/messages')

def api_alarm_routes(config):
    config.add_route('get_alarms', '/{user}', request_method='GET')
    config.add_route('create_alarm', '/{user}', request_method='POST')
    config.add_route('cancel_alarm', '/{user}/{alarmId}', request_method='DELETE')

def api_message_routes(config):
    config.add_route('get_messages', '/{user}', request_method='GET')
    config.add_route('get_next_message', '/{user}/next', request_method='GET')
    config.add_route('get_message', '/{user}/{messageId}', request_method='GET')
    config.add_route('create_message', '/{user}', request_method='POST')
    config.add_route('delete_message', '/{user}/{messageId}', request_method='DELETE')
    config.add_route('set_queue_position', '/{user}/{messageId}/queue/position/{position}', request_method='PUT')
    config.add_route('remove_from_queue', '/{user}/{messageId}/queue/remove', request_method='PUT')
    config.add_route('mark_as_played', '/{user}/{messageId}/played', request_method='PUT')
    config.add_route('mark_as_unplayed', '/{user}/{messageId}/unplayed', request_method='PUT')
    config.add_route('set_as_default', '/{user}/{messageId}/default', request_method='PUT')

