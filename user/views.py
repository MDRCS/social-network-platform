from flask import Blueprint, render_template, session, redirect, url_for, abort, request
import bcrypt
import os
from settings import Config
from werkzeug.utils import secure_filename
import uuid
from user.forms import RegisterForm, LoginForm, EditForm, ForgotForm, PasswordResetForm
from user.models import User
from relationship.models import Relationship
from utils.commons import email
from utils.image_upload import thumbnail_process

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/')
def home():
    return redirect(url_for('.login'))


@user_blueprint.route('/<username>/friends/<int:friends_page_number>', endpoint='profile-friends-page')
@user_blueprint.route('/<username>/friends', endpoint='profile-friends')
@user_blueprint.route('/profile/<string:username>')
def profile(username, friends_page_number=1):
    edit_profile = False
    logged_user = None
    rel = None
    friends_page = False
    friends_per_page = 3
    user = User.getByName(username)
    if user:
        if session['username']:
            logged_user = User.getByName(session['username'])
            rel = Relationship.get_relationship_status(logged_user, user)

            # get user friends
            friends_list = Relationship.get_friends(
                user=logged_user,
                rel_type=Relationship.RELATIONSHIP_TYPE.get(Relationship.FRIENDS),
                status=Relationship.STATUS_TYPE.get(Relationship.APPROVED)
            )

            friends_total = len(friends_list)

            if 'friends' in request.url:
                friends_page = True
                # pagination

                limit = friends_per_page * friends_page_number
                offset = limit - friends_per_page
                if friends_total >= limit:
                    friends = friends_list[offset:limit]
                else:
                    friends = friends_list[offset:friends_total]
            else:
                if friends_list >= 5:
                    friends = friends_list[:5]
                else:
                    friends = friends_list

        if session['username'] and session['username'] == username:
            edit_profile = True

        return render_template('user/profile.html',
                               user=user,
                               logged_user=logged_user,
                               rel=rel,
                               edit_profile=edit_profile,
                               friends=friends,
                               friends_total=friends_total,
                               friends_page=friends_page,
                               )
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
            image_ts = None
            if request.files.get('image'):
                filename = secure_filename(form.image.data.filename)
                folder_path = os.path.join(Config.UPLOAD_FOLDER, 'user_' + user.id)
                file_path = os.path.join(folder_path, filename)
                form.image.data.save(file_path)
                image_ts = str(thumbnail_process(file_path, 'user_' + user.id, str(user.id)))
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
                    email(user.change_configuration['new_email'], "Confirm your new email", body_html, body_text)

            if not error:
                form.populate_obj(user)
                if image_ts:
                    user.profile_image = image_ts
                user.update_record()
                if message:
                    return redirect(url_for('.logout'))
                else:
                    message = "Your info has been updated succefully ..!"

        return render_template('user/edit.html', form=form, error=error, message=message, user=user)

    else:
        abort(404)


@user_blueprint.route('/logout', methods=['GET'])
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
                return redirect(url_for('.profile', username=user.username))
            error = "Incorrect Credentials"
        else:
            error = "Check you email to complete your registration"
    return render_template("user/login.html", form=form, error=error)


@user_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    message = None
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
        email(user.change_configuration['new_email'], "Confirm your email", html_body, html_text)
        message = "Please Check you email to complete registration."
        return render_template('user/register.html', form=form, message=message)
    return render_template('user/register.html', form=form, message=message)


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


@user_blueprint.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None
    message = None
    form = ForgotForm()

    if form.validate_on_submit():
        user = User.getByEmail(form.email.data)
        if user:
            code = str(uuid.uuid4().hex)
            user.change_configuration = {
                "password_reset_code": code,
            }
            user.update_record()
            html_body = render_template('mail/user/password_reset.html', user=user)
            html_text = render_template('mail/user/password_reset.txt', user=user)
            email(user.email, "Password Reset Request", html_body, html_text)
        message = "You will receive a password reset email if we find that email in our system"
    return render_template('user/forgot.html', form=form, message=message, error=error)


# change password when you are not logged in -> from forgot password
@user_blueprint.route('/password_reset/<string:username>/<string:code>', methods=['GET', 'POST'])
def password_reset(username, code):
    require_current = None
    message = None

    form = PasswordResetForm()
    user = User.getByName(username)
    if not user and user.change_configuration.get('password_reset_code') != code:
        abort(404)

    if request.method == 'POST':
        del form.current_password
        if form.validate_on_submit():
            if form.password.data == form.confirm.data:
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(form.password.data, salt)
                user.password = hashed_password
                user.change_configuration = {}
                user.update_record()

                if session.get('username'):
                    session['username'] = ''
                return redirect(url_for('.password_reset_complete'))

    return render_template('user/password_reset.html',
                           form=form,
                           message=message,
                           require_current=require_current,
                           username=username,
                           code=code
                           )


@user_blueprint.route('/password_reset_complete')
def password_reset_complete():
    return render_template('user/password_change_confirmed.html')


# change password when you are logged in
@user_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    require_current = True
    error = None
    form = PasswordResetForm()

    user = User.getByName(username=session.get('username'))
    if not user:
        abort(404)

    if request.method == 'POST':
        if form.validate_on_submit():
            if bcrypt.hashpw(form.current_password.data, user.password) == user.password:
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(form.password.data, salt)
                user.password = hashed_password
                user.update_record()
                # if user is logged in, log him out
                if session.get('username'):
                    session.pop('username')
                return redirect(url_for('.password_reset_complete')), 302
            else:
                error = "Incorrect password"

    return render_template('user/password_reset.html',
                           form=form,
                           require_current=require_current,
                           error=error
                           )
