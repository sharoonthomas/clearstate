# -*- coding: utf-8 -*-
import datetime as dt

from flask.ext.login import UserMixin

from clearstate.extensions import bcrypt
from clearstate.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)


class Role(SurrogatePK, Model):
    __tablename__ = 'roles'

    name = Column(db.String(80), unique=True, nullable=False)
    user_id = ReferenceCol('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    __tablename__ = 'users'

    email = Column(db.String(80), unique=True, nullable=False)
    full_name = Column(db.String(50), nullable=True)

    #: The hashed password
    password = Column(db.String(128), nullable=True)

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, email, password=None, **kwargs):
        db.Model.__init__(self,email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def __repr__(self):
        return '<User({email!r})>'.format(email=self.email)


def users_exist():
    """
    Returns True if atleast one user exists in the database
    """
    return (User.query.first() is not None)
