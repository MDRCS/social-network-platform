from flask import Flask
from utils.database import Database


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')

    from user.views import user_blueprint
    app.register_blueprint(user_blueprint)

    return app
