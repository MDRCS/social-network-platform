from flask_wtf import Form
from wtforms import validators, StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError
from user.models import User





class RegisterForm(Form):
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])

    email = EmailField('Email', [
        validators.DataRequired(),
        validators.email()
    ])

    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=4, max=25)
    ])

    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.equal_to('confirm', message='Password Must Match'),
        validators.length(min=4, max=80)
    ])

    confirm = PasswordField('Repeat Password')

    def validate_username(form, field):
        if User.getByName(field.data):
            raise ValidationError("This Username already exist ..!")

    def validate_email(form, field):
        if User.getByEmail(field.data):
            raise ValidationError("This Email already registred ..!")
