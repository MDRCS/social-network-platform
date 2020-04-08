from flask import Blueprint

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/')
def index():
    return "You hurt me ! .."
