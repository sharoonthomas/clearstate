# -*- coding: utf-8 -*-
import pytest

from clearstate.public.forms import LoginForm
from clearstate.user.forms import RegisterForm
from .factories import UserFactory


class TestRegisterForm:

    def test_validate_email_already_registered(self, user):
        # enters email that is already registered
        form = RegisterForm(
            email=user.email,
            password='example',
            confirm='example'
        )

        assert form.validate() is False
        assert 'Email already registered' in form.email.errors

    def test_validate_success(self, db):
        form = RegisterForm(
            email='new@test.test',
            password='example',
            confirm='example'
        )
        assert form.validate() is True


class TestLoginForm:

    def test_validate_success(self, user):
        user.set_password('example')
        user.save()
        form = LoginForm(email=user.email, password='example')
        assert form.validate() is True
        assert form.user == user

    def test_validate_invalid_password(self, user):
        user.set_password('example')
        user.save()
        form = LoginForm(email=user.email, password='wrongpassword')
        assert form.validate() is False
        assert 'Invalid password' in form.password.errors

    def test_validate_inactive_user(self, user):
        user.active = False
        user.set_password('example')
        user.save()
        # Correct username and password, but user is not activated
        form = LoginForm(email=user.email, password='example')
        assert form.validate() is False
        assert 'User not activated' in form.email.errors
