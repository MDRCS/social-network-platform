import unittest
import os
from flask import session
from app import create_app as create_app_test
from utils.database import Database
from user.models import User
from relationship.models import Relationship


class FeedTest(unittest.TestCase):

    def create_app(self):
        return create_app_test(
            'testing'
        )

    def setUp(self) -> None:
        self.app_factory = self.create_app()
        self.db_name = os.environ['MONGODB_NAME']
        self.app = self.app_factory.test_client()

    def tearDown(self) -> None:
        db = Database.CLIENT
        db.drop_database(self.db_name)

    def getUser1(self):
        return dict(
            first_name="Mohamed",
            last_name="El Rahali",
            username="mdrahali",
            email="mdr.ga99@gmail.com",
            password="12345",
            confirm="12345"
        )

    def getUser2(self):
        return dict(
            first_name="Jorge",
            last_name="Bert",
            username="jorge_1",
            email="elrahali.md@gmail.com",
            password="12345",
            confirm="12345"
        )

    def getUser3(self):
        return dict(
            first_name="Omar",
            last_name="Marine",
            username="omar_mar1",
            email="mohammad.el-rahali@uha.fr",
            password="12345",
            confirm="12345"
        )

    def test_feed_posts(self):
        """
            Registeration:  User 1
        """
        user_1 = self.getUser1()
        self.app.post("/register", data=user_1, follow_redirects=True)
        user_1 = User.getByName(username=user_1['username'])
        code = user_1.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_1.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)
        """
            Login: User 1
        """

        self.app.post('/login', data=dict(
            username=user_1.username,
            password=self.getUser1()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_1.username

        # post a message on my own wall
        self.app.post('/message/add', data=dict(
            to_user=user_1.username,
            post="Test First Post From User 1",
            images=[]
        ), follow_redirects=True)

        # register user #2


        # make friends with user #2


        # login user #2 and confirm friend user #1

        # login the first user again


        # post a message


        # post a message to user 2


        # login the second user

        # register user #3


        # make friends with user #2


        # login the first user


        # block user 3


        # login the second user

        # user 2 confirm friend user 3

        # post a message to user 3


        # login the first user


        # check he doesn't see user 2's post to user 3 (blocked)

