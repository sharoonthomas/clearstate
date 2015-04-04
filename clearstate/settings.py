# -*- coding: utf-8 -*-
import os

os_env = os.environ


class Config(object):
    SECRET_KEY = os_env.get('CLEARSTATE_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False

    # Debug toolbar
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar

    # Enforce following from environment
    SECRET_KEY = os_env.get('CLEARSTATE_SECRET')
    SQLALCHEMY_DATABASE_URI = os_env.get('SQLALCHEMY_DATABASE_URI')


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'

    if 'SQLALCHEMY_DATABASE_URI' not in os_env:
        print "No SQLALCHEMY_DATABASE_URI in environment"
        # Put the db file in project root
        DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)

    # Enable the debug toolbar
    DEBUG_TB_ENABLED = True

    # Don't bundle/minify static assets
    ASSETS_DEBUG = True

    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing
