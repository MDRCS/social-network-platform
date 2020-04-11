from flask import Blueprint, render_template, session, redirect, url_for, abort
import bcrypt
from user.forms import RegisterForm, LoginForm, EditForm
from user.models import User

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/ed')
def ed():
    return render_template('user/edit.html')


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


@user_blueprint.route('/edit', methods=('POST', 'GET'))
def edit():
    error = None
    message = None
    user = User.getByName(session['username'])
    if user:
        form = EditForm(obj=user)
        if form.validate_on_submit():
            if user.username != form.username.data.lower() or user.email != form.email.data.lower():
                if user.username != form.username.data and User.getByName(form.username.data.lower()):
                    error = "This username is already in use."
                else:
                    session['username'] = form.username.data.lower()
                    user.username = form.username.data.lower()

                if user.email != form.email.data.lower() and User.getByEmail(form.email.data.lower()):
                    error = "This email is already in use."
                else:
                    user.email = form.email.data.lower()

            if not error:
                form.populate_obj(user)
                user.update_record()
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


@user_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.getByName(form.username.data)

        if user and bcrypt.hashpw(form.password.data, user.password) == user.password:
            session['username'] = user.username
            return redirect(url_for('.profile', username=user.username))
        error = "Incorrect Credentials"
    return render_template("user/login.html", form=form, error=error)


@user_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        user = User(username=form.username.data,
                    password=hashed_password,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    bio=form.bio.data)
        user.save_database()
        return "User is registred Successfuly"
    return render_template('user/register.html', form=form)
