# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, current_app, \
     request, flash
from flask.ext.login import login_required, login_user

from clearstate.user.forms import RegisterForm
from clearstate.user.models import User, users_exist
from clearstate.utils import flash_errors

blueprint = Blueprint(
    "user", __name__, url_prefix='/users', static_folder="../static"
)


@blueprint.route("/")
@login_required
def members():
    return render_template("users/members.html")


def check_if_setup_done():
    """
    Check if the initial setup has been performed.
    """
    if request.path == url_for('user.initial_setup'):
        return
    if not users_exist():
        return redirect(url_for('user.initial_setup'))


@blueprint.route("/initial-setup", methods=['GET', 'POST'])
def initial_setup():
    """
    Allow initial setup to be done.

    This is allowed only if there are no users currently in the User table.
    Seems like a fairly good way to determine if the app is being run for the
    first time.
    """
    if users_exist():
        # Do not allow initial_setup to happen when users already exist
        # in the database.
        current_app.logger.info('Cannot run initial-setup when users exist.')
        return redirect(url_for('public.login'))

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        new_user = User.create(
            full_name=form.full_name.data,
            email=form.email.data,
            password=form.password.data,
            active=True
        )
        login_user(new_user)
        return redirect(url_for('pages.pages'))
    else:
        flash_errors(form)
    return render_template('users/initial-setup.html', form=form)
