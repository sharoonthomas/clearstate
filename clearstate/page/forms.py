# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from clearstate.page.models import timezones


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
