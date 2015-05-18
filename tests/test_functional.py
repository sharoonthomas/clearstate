# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import pytest
from flask import url_for


from clearstate.user.models import User
from clearstate.page.models import Page


class TestLoggingIn:

    def test_can_log_in_returns_200(self, user, testapp):
        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['email'] = user.email
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        res = testapp.get("/")
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['email'] = user.email
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for('public.logout')).follow()
        # sees alert
        assert 'You are logged out.' in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['email'] = user.email
        form['password'] = 'wrong'
        # Submits
        res = form.submit()
        # sees error
        assert "Invalid password" in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['email'] = 'unknown'
        form['password'] = 'myprecious'
        # Submits
        res = form.submit()
        # sees error
        assert "Unknown user" in res


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


class TestPage:

    def test_deletion(self, user, page, testapp):
        res = testapp.post(
            '/login',
            {
                'email': user.email,
                'password': 'myprecious',
            }
        )

        delete_url = '/pages/%d/delete' % page.id
        res = testapp.get(delete_url)

        # Fill form with wrong name
        form = res.forms['delete-page-form']
        form['name'] = 'not-page-name'
        res = form.submit()
        assert 'Name should match the page name' in res

        res = testapp.get(delete_url)
        # Fill with correct name
        form = res.forms['delete-page-form']
        form['name'] = page.name
        res = form.submit().follow()

        assert Page.query.count() == 0


class TestIncident:

    def test_creation(self, user, page, testapp):
        res = testapp.post(
            '/login',
            {
                'email': user.email,
                'password': 'myprecious',
            }
        )
        add_incident_url = '/pages/%d/incidents/add' % page.id
        res = testapp.get(add_incident_url)

        # Fill the form up
        form = res.forms['create-incident-form']
        form['title'] = 'Build processing delayed'
        form['status'] = 'Investigating'
        form['message'] = 'A bad deploy is causing backups.....'
        res = form.submit().follow()

        assert page.incident_count == 1
        incident, = page.incidents

        assert len(incident.updates) == 1
        assert incident.title == 'Build processing delayed'
        assert incident.message == 'A bad deploy is causing backups.....'
        assert incident.status == 'Investigating'

        # Now post a status update
        update_incident_url = '/pages/%d/incidents/%d' % (
            page.id, incident.id
        )
        res = testapp.get(update_incident_url)

        # Fill the form up
        form = res.forms['update-incident-form']
        form['status'] = 'Fixed'
        form['message'] = 'The deploy has been reverted.'
        res = form.submit().follow()

        assert page.incident_count == 1
        incident, = page.incidents

        assert len(incident.updates) == 2
        assert incident.title == 'Build processing delayed'
        assert incident.message == 'The deploy has been reverted.'
        assert incident.status == 'Fixed'
