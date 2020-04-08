from flask import Blueprint, render_template
import bcrypt
from user.forms import RegisterForm
from user.models import User

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/')
def index():
    return "You hurt me ! .."


@user_blueprint.route('/home')
def home():
    return "You hurt me ! .."


@user_blueprint.route('/profile')
def profile():
    return "You hurt me ! .."


@user_blueprint.route('/edit')
def edit():
    return "You hurt me ! .."


@user_blueprint.route('/change_password')
def change_password():
    return "You hurt me ! .."


@user_blueprint.route('/logout')
def logout():
    return "You hurt me ! .."


@user_blueprint.route('/login')
def login():
    return "You hurt me ! .."


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
                    last_name=form.last_name.data)
        user.save_database()
        return "User is registred Successfuly"
    return render_template('user/register.html', form=form)
