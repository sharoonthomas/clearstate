#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import MigrateCommand

from clearstate.app import create_app
from clearstate.user.models import User
from clearstate.settings import DevConfig, ProdConfig
from clearstate.database import db

if os.environ.get("CLEARSTATE_ENV") == 'prod':
    app = create_app(ProdConfig)
    app.logger.info('Loading with production config')
else:
    app = create_app(DevConfig)
    app.logger.info('Loading with development config')

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '--verbose'])
    return exit_code


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
