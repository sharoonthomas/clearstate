from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import User


class RegisterForm(Form):
    email = TextField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Verify password',
        [DataRequired(), EqualTo('password', message='Passwords must match')]
    )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True
