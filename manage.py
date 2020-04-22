import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from user.models import User
from relationship.models import Relationship
from feed.models import Feed, Message

app = create_app(os.environ.get('environment'))


@app.shell_context_processor
def make_shell_context():
    return dict(User=User, Relationship=Relationship, Feed=Feed,
                Message=Message)

