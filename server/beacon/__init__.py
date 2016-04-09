
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.request import Request
from pyramid.request import Response

from pyramid.session import SignedCookieSessionFactory

from .models import (
    DBSession,
    Base,
    )

def request_factory(environ):
    request = Request(environ)
    if request.is_xhr:
        request.response = Response()
        request.response.headerlist = []
        request.response.headerlist.extend(
            (
                ('Access-Control-Allow-Origin', '*'),
                #('Content-Type', 'application/json')
            )
        )
    return request

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    secret = config.get_settings().get('beacon.secret')
    if not secret:
        secret = 'yellr_secret'
    httponly = False if config.get_settings().get('beacon.header_httponly') == 'false' else True
    secure = False if config.get_settings().get('beacon.header_secure') == 'false' else True
    my_session_factory = SignedCookieSessionFactory(
        secret,
        httponly=httponly,
        secure=secure,
    )
    config.set_session_factory(my_session_factory)

    # enables cors so the app can do AJAX calls.
    config.set_request_factory(request_factory)


    # end points
    config.add_route('/', '/')

    # api access
    config.add_route('/api/users/login', '/api/users/login')
    config.add_route('/api/users/logout', '/api/users/logout')
    config.add_route('/api/users', '/api/users')
    config.add_route('/api/users/{id}', '/api/users/{id}')    

    config.add_route('/api/topics', '/api/topics')
    #config.add_route('/api/topics/{id}', '/api/topics/{id}')

    config.add_route('/api/groups', '/api/groups')
    config.add_route('/api/groups/{id}', '/api/groups/{id}')

    config.add_route('/api/beacons', '/api/beacons')
    config.add_route('/api/beacons/{id}', '/api/beacons/{id}')
        
    #config.add_route('/api/beacon_topics', '/api/beacon_topics')
    #config.add_route('/api/beacon_topics/{id}', '/api/beacon_topics/{id}')

    config.scan()
    return config.make_wsgi_app()
