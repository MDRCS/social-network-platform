from flask import Blueprint, render_template, session, redirect, url_for, abort
import bcrypt
import os
import uuid
from user.forms import RegisterForm, LoginForm, EditForm
from user.models import User
from utils.commons import email

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/')
def home():
    return "You hurt me ! .."


@user_blueprint.route('/profile/<string:username>', methods=['GET'])
def profile(username):
    edit_profile = False
    user = User.getByName(username)
    if session['username'] and session['username'] == username:
        edit_profile = True
        return render_template('user/profile.html', user=user, edit_profile=edit_profile)
    if user:
        return render_template('user/profile.html', user=user, edit_profile=edit_profile)
    else:
        abort(404)


@user_blueprint.route('/edit', methods=['POST', 'GET'])
def edit():
    error = None
    message = None
    user = User.getByName(session['username'])
    if user:
        form = EditForm(obj=user)
        if form.validate_on_submit():
            if user.username != form.username.data.lower():
                if User.getByName(form.username.data.lower()):
                    error = "This username is already in use."
                else:
                    session['username'] = form.username.data.lower()
                    user.username = form.username.data.lower()

            if user.email != form.email.data.lower():
                if User.getByEmail(form.email.data.lower()):
                    error = "This email is already in use."
                else:
                    code = str(uuid.uuid4())

                    user.change_configuration = {
                        "new_email": form.email.data.lower(),
                        "confirmation_code": code
                    }

                    user.email_confirmation = False
                    message = "You will need to confirm the new email to complete this change"

                    # email the user
                    body_html = render_template('mail/user/change_email.html', user=user)
                    body_text = render_template('mail/user/change_email.txt', user=user)
                    # email(user.change_configuration['new_email'], "Confirm your new email", body_html, body_text)

            if not error:
                form.populate_obj(user)
                user.update_record()
                if message:
                    return redirect(url_for('.logout')), 302
                else:
                    message = "Your info has been updated succefully ..!"

        return render_template('user/edit.html', form=form, error=error, message=message, user=user)

    else:
        abort(404)


@user_blueprint.route('/change_password')
def change_password():
    return "You hurt me ! .."


@user_blueprint.route('/forgot')
def forgot():
    return "You hurt me ! .."


@user_blueprint.route('/logout', methods=('GET', 'POST'))
def logout():
    session['username'] = ''
    return redirect(url_for('.login'))


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.getByName(form.username.data)
        if user.email_confirmation:
            if user and bcrypt.hashpw(form.password.data, user.password) == user.password:
                session['username'] = user.username
                return redirect(url_for('.profile', username=user.username)), 200
            error = "Incorrect Credentials"
        else:
            error = "Check you email to complete your registration"
    return render_template("user/login.html", form=form, error=error)


@user_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        code = str(uuid.uuid4().hex)
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        user = User(username=form.username.data,
                    password=hashed_password,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    bio=form.bio.data,
                    change_configuration={
                        "new_email": form.email.data.lower(),
                        "confirmation_code": code
                    })
        user.save_database()
        # send email
        html_body = render_template('mail/user/register.html', user=user)
        html_text = render_template('mail/user/register.txt', user=user)
        # email(user.change_configuration['new_email'], "Confirm your email", html_body, html_text)
        return "User is registred Successfuly"
    return render_template('user/register.html', form=form)


@user_blueprint.route('/confirm/<string:username>/<string:code>', methods=('GET', 'POST'))
def confirm(username, code):
    user = User.getByName(username)
    if user and user.change_configuration and user.change_configuration.get("confirmation_code"):
        if user.change_configuration.get("confirmation_code") == code:
            user.email = user.change_configuration.get("new_email")
            user.change_configuration = {}
            user.email_confirmation = True
            user.update_record()
            return render_template('user/email_confirmed.html')
    else:
        abort(404)
