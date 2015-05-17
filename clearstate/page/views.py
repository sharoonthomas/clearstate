# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask.ext.login import login_required

from clearstate.page.models import Page, Component, ComponentGroup, Incident
from clearstate.page.forms import PageForm, ComponentForm, \
    ComponentGroupForm, IncidentForm, PageDeleteForm
from clearstate.utils import flash_errors

blueprint = Blueprint(
    "pages", __name__, url_prefix='/pages', static_folder="../static"
)


def get_timezone_from_page():
    """
    This function looks into the current request to see if there is a page_id
    in the url parameters. If there is one, it returns the timezone or returns
    UTC.
    """
    if request.view_args is not None and 'page_id' in request.view_args:
        page_id = request.view_args['page_id']
        return Page.get_by_id(page_id).timezone
    return 'UTC'


@blueprint.route("/")
@login_required
def pages():
    """
    Display existing pages.
    If there are no pages, redirect to an initial-setup page
    """
    pages = Page.query.all()
    return render_template("pages/pages.html", pages=pages)


@blueprint.route("/add", methods=['GET', 'POST'])
@login_required
def add_page():
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

    return render_template("pages/create-page.html", pages=pages, form=form)


@blueprint.route('/<int:page_id>')
def render_status_page(page_id):
    """
    Render the given status page.

    This handler is invoked to view the page in the case of multiple pages
    with the decorated URL. The other way to reach here is through a sub
    handler.
    """
    page = Page.get_by_id(page_id)

    # Paginating past incidents
    till_date = datetime.today()
    if 'date' in request.args:
        try:
            till_date = datetime.strptime(request.args['date'], '%Y-%m-%d')
        except ValueError:
            pass

    incidents = page.get_incidents(till_date, 10)
    return render_template(
        'pages/public-page.html', page=page, incidents=incidents
    )


@blueprint.route('/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(page_id):
    """
    Edit the status page
    """
    page = Page.get_by_id(page_id)

    form = PageForm(request.form, obj=page)
    if form.validate_on_submit():
        form.populate_obj(page)
        page.save()
        flash('Form has been updated', 'success')
        return redirect(
            url_for('pages.dashboard', page_id=page.id)
        )
    else:
        flash_errors(form)
    return render_template('pages/edit.html', page=page, form=form)


@blueprint.route('/<int:page_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(page_id):
    """
    Delete the status page
    """
    page = Page.get_by_id(page_id)

    form = PageDeleteForm(request.form, obj=page)
    if form.validate_on_submit():
        page.delete()
        flash('Form has been deleted', 'success')
        return redirect(
            url_for('pages.pages')
        )
    else:
        flash_errors(form)

    return render_template('pages/delete.html', page=page, form=form)


@blueprint.route('/<int:page_id>/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard(page_id):
    """
    Render the given status page's dashboard.
    """
    page = Page.get_by_id(page_id)

    # TODO: Implement posting of component status
    return render_template('pages/dashboard.html', page=page)


@blueprint.route('/<int:page_id>/components')
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
    '/<int:page_id>/components/update-status',
    methods=['POST'])
@login_required
def update_component_status(page_id):
    """
    Update a component't status
    """
    page = Page.get_by_id(page_id)
    component = Component.get_by_id(int(request.form['component']))
    assert component.page == page

    component.status = request.form['status']
    component.save()

    if request.is_xhr:
        return 'OK'

    return redirect(url_for('pages.dashboard', page_id=page_id))


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


@blueprint.route('/<int:page_id>/incidents')
@blueprint.route('/<int:page_id>/incidents/<int:page_no>')
@login_required
def incidents(page_id, page_no=1):
    """
    Render the given status page's dashboard.

    :param page_id: The ID of the status page
    :param page_no: The pagination page number
    """
    page = Page.get_by_id(page_id)

    incidents = Incident.query.filter(
        Incident.page_id == page_id
    ).order_by(Incident.create_time.desc()).paginate(page_no, 5)

    return render_template(
        'pages/incidents.html', page=page, incidents=incidents
    )


@blueprint.route('/<int:page_id>/incidents/add', methods=['GET', 'POST'])
@login_required
def add_incident(page_id):
    """
    Show form and add incident on POST.
    """
    page = Page.get_by_id(page_id)

    # TODO: Allow updating component status's along with this.
    form = IncidentForm(request.form)

    if form.validate_on_submit():
        incident = Incident()
        form.populate_obj(incident)
        incident.page_id = page_id
        incident.save()
        flash('Incident has been added to the status page', 'success')
        return redirect(
            url_for('pages.incidents', page_id=page_id)
        )
    else:
        flash_errors(form)
    return render_template(
        'pages/create-incident.html', page=page, form=form
    )


@blueprint.route(
    '/<int:page_id>/incidents/<int:incident_id>/edit',
    methods=['GET', 'POST'])
@login_required
def edit_incident(page_id, incident_id):
    """
    Allow editing incident
    """
    incident = Incident.get_by_id(incident_id)
    page = incident.page

    form = IncidentForm(request.form, obj=incident)

    if form.validate_on_submit():
        form.populate_obj(incident)
        incident.save()
        flash('Incident has been updated', 'success')
        return redirect(
            url_for('pages.incidents', page_id=page_id)
        )
    else:
        flash_errors(form)
    return render_template(
        'pages/edit-incident.html', page=page, form=form
    )
