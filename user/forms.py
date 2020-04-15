from flask_wtf import form
from wtforms import validators, StringField, PasswordField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError
from user.models import User


class BaseUserForm(form.FlaskForm):
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])

    email = EmailField('Email', [
        validators.DataRequired(),
        validators.Email()
    ])

    username = StringField('Username', [
        validators.DataRequired(),
        validators.Regexp('^[a-zA-Z0-9_-]{4,25}$', message="Username must contain only letters numbers or underscore"),
        validators.length(min=4, max=25)
    ])

    bio = StringField('Bio',
                      widget=TextArea(),
                      validators=[validators.Length(max=160)]
                      )


class PasswordForm(form.FlaskForm):
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.equal_to('confirm', message='Password Must Match'),
        validators.length(min=4, max=80)
    ])

    confirm = PasswordField('Repeat Password')


class RegisterForm(BaseUserForm, PasswordForm):

    def validate_username(form, field):
        if User.getByName(field.data):
            raise ValidationError("This Username already exist ..!")

    def validate_email(form, field):
        if User.getByEmail(field.data):
            raise ValidationError("This Email already registred ..!")


class LoginForm(form.FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=4, max=25)
    ])

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=4, max=80)
    ])


class EditForm(BaseUserForm):
    pass


class ForgotForm(form.FlaskForm):
    email = EmailField('Email', [
        validators.DataRequired(),
        validators.Email()
    ])


class PasswordResetForm(PasswordForm):
    current_password = PasswordField('Current Password', [
        validators.DataRequired(),
        validators.length(min=4, max=80)
    ])
