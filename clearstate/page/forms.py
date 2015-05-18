# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired, URL, Optional, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from clearstate.page.models import timezones, IncidentUpdate


class PageForm(Form):
    name = TextField(
        'Name', validators=[DataRequired()])
    site_url = TextField(
        'Site URL', validators=[DataRequired()]
    )
    about_page = TextAreaField('About this status page')
    timezone = SelectField(
        'Timezone', choices=zip(timezones, timezones),
        validators=[DataRequired()]
    )


class ComponentForm(Form):
    name = TextField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    link = TextField('Link', validators=[Optional(), URL()])
    group = QuerySelectField('Group', allow_blank=True, get_label='name')


class ComponentGroupForm(Form):
    name = TextField('Name', validators=[DataRequired()])


class EditIncidentForm(Form):
    title = TextField('Title', validators=[DataRequired()])


class UpdateIncidentForm(Form):
    # TODO: Replace with radio field that is more appropriate
    status = SelectField(
        'Status', choices=zip(
            IncidentUpdate.statuses, IncidentUpdate.statuses
        ),
        validators=[DataRequired()]
    )
    message = TextAreaField('Message', validators=[DataRequired()])


class IncidentForm(EditIncidentForm, UpdateIncidentForm):
    pass


class PageDeleteForm(Form):
    name = TextField('Name', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        # Store the name of the page (obj) locally
        self.page_name = kwargs.pop('obj').name
        super(PageDeleteForm, self).__init__(*args, **kwargs)

    def validate_name(self, field):
        if field.data.lower() != self.page_name.lower():
            raise ValidationError('Name should match the page name')
