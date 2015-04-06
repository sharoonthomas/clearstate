# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
from flask import (
    Blueprint, request, render_template, flash, url_for,
    redirect, session
)
from flask.ext.login import login_user, login_required, logout_user

from clearstate.extensions import login_manager
from clearstate.user.models import User, users_exist
from clearstate.page.models import Page
from clearstate.public.forms import LoginForm
from clearstate.user.forms import RegisterForm
from clearstate.utils import flash_errors
from clearstate.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET"])
def home():
    """
    The home page by default is expected to serve the status page, identified
    from the host name.
    """
    # TODO: Find status page from host name

    # If there are no matches, are there any pages or users at all ?
    if not users_exist():
        return redirect(url_for('user.initial_setup'))
    else:
        return redirect(url_for('pages.pages'))


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or \
                url_for("pages.pages")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/login.html", form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(
            email=form.email.data,
            password=form.password.data,
            active=True
        )
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
