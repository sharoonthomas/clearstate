# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import pytest
from flask import url_for


from clearstate.user.models import User
from .factories import UserFactory


class TestRegistering:

    def test_can_register(self, user, testapp):
        old_count = len(User.query.all())
        # Goes to homepage
        res = testapp.get("/")
        # Fills out the form
        form = res.forms["registerForm"]
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secret'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        # Goes to registration page
        res = testapp.get(url_for("public.register"))
        # Fills out form, but passwords don't match
        form = res.forms["registerForm"]
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secrets'
        # Submits
        res = form.submit()
        # sees error message
        assert "Passwords must match" in res
