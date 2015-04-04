# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request
from flask.ext.login import login_required

from clearstate.extensions import db
from clearstate.page.models import Page
from clearstate.page.forms import PageForm

blueprint = Blueprint(
    "pages", __name__, url_prefix='/pages', static_folder="../static"
)


@blueprint.route("/", methods=['GET', 'POST'])
@login_required
def pages():
    """
    Display existing pages.
    If there are no pages, redirect to an initial-setup page
    """
    pages = db.query(Page).all()
    if request.method == 'GET' and not pages:
        return redirect(url_for('page.initial_setup'))

    form = PageForm(request.form)
    if form.validate_on_submit():
        new_page = Page.create(
            name=form.name.data,
            site_url=form.site_url.data,
            about_page=form.about_page.data,
            timezone=form.timezone.data,
        )
        return redirect(
            url_for('pages.render_status_page', page_id=new_page.id)
        )
    return render_template("pages/pages.html", pages=pages)


@blueprint.route("/initial-setup")
@login_required
def initial_setup():
    """
    Show a friendlier page for creating the first status page.
    """
    pass


@blueprint.route('/<int:page_id>')
def render_status_page(page_id):
    """
    Render the given status page.

    This handler is invoked to view the page in the case of multiple pages
    with the decorated URL. The other way to reach here is through a sub
    handler.
    """
    page = Page.get_by_id(page_id)
    return render_template('pages/status-page.html', page=page)
