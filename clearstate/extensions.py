# -*- coding: utf-8 -*-
"""
Extensions module.

Each extension is initialized in the app factory located in app.py
"""

from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.migrate import Migrate
migrate = Migrate()

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.debugtoolbar import DebugToolbarExtension
debug_toolbar = DebugToolbarExtension()


from flask.ext.gravatar import Gravatar
gravatar = Gravatar(
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=True,
    base_url=None
)


from flask.ext.babel import Babel
babel = Babel()
