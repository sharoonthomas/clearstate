# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL
from clearstate.page.models import timezones


class PageForm(Form):
    name = TextField(
        'Name', validators=[DataRequired()])
    site_url = TextField(
        'Site URL', validators=[DataRequired(), URL()]
    )
    about_page = TextAreaField('About this status page')
    timezone = SelectField(
        'Timezone', choices=zip(timezones, timezones),
        validators=[DataRequired()]
    )
