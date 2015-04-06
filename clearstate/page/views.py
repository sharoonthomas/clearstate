# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask.ext.login import login_required

from clearstate.extensions import db
from clearstate.page.models import Page, Component, ComponentGroup
from clearstate.page.forms import PageForm, ComponentForm, ComponentGroupForm
from clearstate.utils import flash_errors

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
    form = PageForm(request.form)
    if form.validate_on_submit():
        new_page = Page.create(
            name=form.name.data,
            site_url=form.site_url.data,
            about_page=form.about_page.data,
            timezone=form.timezone.data,
        )
        return redirect(
            url_for('pages.dashboard', page_id=new_page.id)
        )
    else:
        flash_errors(form)

    # TODO: Paginate if someone has too many pages
    pages = Page.query.all()

    return render_template("pages/pages.html", pages=pages, form=form)


@blueprint.route('/<int:page_id>')
def render_status_page(page_id):
    """
    Render the given status page.

    This handler is invoked to view the page in the case of multiple pages
    with the decorated URL. The other way to reach here is through a sub
    handler.
    """
    page = Page.get_by_id(page_id)
    return render_template('pages/public-page.html', page=page)


@blueprint.route('/<int:page_id>/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard(page_id):
    """
    Render the given status page's dashboard.
    """
    page = Page.get_by_id(page_id)

    # TODO: Implement posting of component status
    return render_template('pages/dashboard.html', page=page)


@blueprint.route('/<int:page_id>/components', methods=['GET', 'POST'])
@login_required
def components(page_id):
    """
    Render the given status page's dashboard.
    """
    page = Page.get_by_id(page_id)
    return render_template('pages/components.html', page=page)


@blueprint.route('/<int:page_id>/components/add', methods=['GET', 'POST'])
@login_required
def add_component(page_id):
    """
    Render the given status page's dashboard.
    """
    page = Page.get_by_id(page_id)

    form = ComponentForm(request.form)
    form.group.query = ComponentGroup.query.filter(page_id == page.id)

    if form.validate_on_submit():
        component = Component()
        form.populate_obj(component)
        component.page_id = page_id
        component.save()
        flash('Component has been added to the status page', 'success')
        return redirect(
            url_for('pages.components', page_id=page_id)
        )
    else:
        flash_errors(form)
    return render_template(
        'pages/create-component.html', page=page, form=form
    )


@blueprint.route(
    '/<int:page_id>/components/<int:component_id>/edit',
    methods=['GET', 'POST'])
@login_required
def edit_component(page_id, component_id):
    """
    Allow editing component
    """
    component = Component.get_by_id(component_id)
    page = component.page

    form = ComponentForm(request.form, obj=component)
    form.group.query = ComponentGroup.query.filter(page_id == page.id)

    if form.validate_on_submit():
        print component.group
        form.populate_obj(component)
        print component.group
        component.save()
        flash('Component has been updated', 'success')
        return redirect(
            url_for('pages.components', page_id=page_id)
        )
    else:
        flash_errors(form)
    return render_template(
        'pages/edit-component.html', page=page, form=form
    )


@blueprint.route('/<int:page_id>/component-groups/add', methods=['GET', 'POST'])
@login_required
def add_component_group(page_id):
    """
    Render the given status page's dashboard.
    """
    page = Page.get_by_id(page_id)
    form = ComponentGroupForm(request.form)
    if form.validate_on_submit():
        ComponentGroup.create(
            name=form.name.data,
            page_id=page_id,
        )
        flash('Component Group has been added to the status page', 'success')
        return redirect(
            url_for('pages.components', page_id=page_id)
        )
    else:
        flash_errors(form)
    return render_template(
        'pages/create-component-group.html', page=page, form=form
    )
