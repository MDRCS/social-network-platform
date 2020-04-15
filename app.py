from flask import Flask
import os
from settings import config


def create_app(envi_conf='default'):
    app = Flask(__name__)
    app.config.from_object(config[envi_conf])
    os.environ['MONGODB_NAME'] = app.config['MONGODB_NAME']
    os.environ['DATABASE_URI'] = os.environ.get('HOST') + app.config['MONGODB_NAME']
    from user.views import user_blueprint
    app.register_blueprint(user_blueprint)

    return app
