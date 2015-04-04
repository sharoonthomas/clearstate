# -*- coding: utf-8 -*-
from factory import Sequence, PostGenerationMethodCall
from factory.alchemy import SQLAlchemyModelFactory

from clearstate.user.models import User
from clearstate.database import db


class BaseFactory(SQLAlchemyModelFactory):

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        model = User
