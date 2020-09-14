import zope
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

def get_session_factory(engine):
    """Return a generator of database session objects."""
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory

def get_tm_session(session_factory, transaction_manager):
    """Build a session and register it as a transaction-managed session."""
    dbsession = session_factory()
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    #settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    #session_factory = get_session_factory(engine_from_config(settings, prefix='sqlalchemy.'))

    my_session_factory = SignedCookieSessionFactory('itsaseekreet')

    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.include('cornice')
        #config.include('pyramid_tm')
        config.scan()
        config.set_session_factory(my_session_factory)

        """   config.registry['dbsession_factory'] = session_factory
                config.add_request_method(
                    lambda request: get_tm_session(session_factory, request.tm),
                    'dbsession',
                    reify=True
                )"""

    return config.make_wsgi_app()
