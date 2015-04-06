# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from clearstate.user.models import User, Role
from clearstate.page.models import Component
from .factories import UserFactory, PageFactory


@pytest.mark.usefixtures('db')
class TestUser:

    def test_get_by_id(self):
        user = User('foo', 'foo@bar.com')
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        user = User(email='foo@bar.com')
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        user = User(email='foo@bar.com')
        user.save()
        assert user.password is None

    def test_factory(self, db):
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password('myprecious')

    def test_check_password(self):
        user = User.create(
            email="foo@bar.com",
            password="foobarbaz123"
        )
        assert user.check_password('foobarbaz123') is True
        assert user.check_password("barfoobaz") is False

    def test_roles(self):
        role = Role(name='admin')
        role.save()
        u = UserFactory()
        u.roles.append(role)
        u.save()
        assert role in u.roles


@pytest.mark.usefixtures('db')
class TestPage:

    def test_factory(self, db):
        page = PageFactory()
        db.session.commit()

        assert bool(page.name)
        assert bool(page.site_url)
        assert page.active is True
        assert page.timezone == 'UTC'
        assert page.component_groups == []
        assert page.components == []

    def test_component_count(self, db):
        page = PageFactory()
        page.save()

        assert page.component_count == 0

        for name in ['c1', 'c2', 'c3', 'c4']:
            component = Component(
                name=name,
                page_id=page.id
            )
            component.save()

        assert page.component_count == 4
