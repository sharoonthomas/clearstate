# -*- coding: utf-8 -*-
from factory import Sequence, PostGenerationMethodCall
from factory.alchemy import SQLAlchemyModelFactory

from clearstate.user.models import User
from clearstate.page.models import Page
from clearstate.database import db


class BaseFactory(SQLAlchemyModelFactory):

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True
    full_name = "Spock"

    class Meta:
        model = User


class PageFactory(BaseFactory):

    name = Sequence(lambda n: "Page {0}".format(n))
    site_url = 'demo.clearstate.io'
    about_page = 'Some random text'
    timezone = 'UTC'
    active = True

    class Meta:
        model = Page
