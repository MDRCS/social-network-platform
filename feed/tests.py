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

        """
             post a message on my own wall as User 1
        """

        response = self.app.post('/message/add', data=dict(
            to_user=user_1.username,
            post="Test First Post From User 1",
            images=[]
        ), follow_redirects=True)

        assert "Test First Post From User 1" in str(response.data)

        """
            Registeration:  User 2
        """
        user_2 = self.getUser2()
        self.app.post("/register", data=user_2, follow_redirects=True)
        user_2 = User.getByName(username=user_2['username'])
        code = user_2.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_2.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        """
            Make a Friendship Request to User 2
        """
        response = self.app.get('/add_friend/' + user_2.username, follow_redirects=True)
        assert "Friendship Requested" in str(response.data)

        """
            Login as User 2
            Confirm Friendship request from User 1
        """

        self.app.post('/login', data=dict(
            username=user_2.username,
            password=self.getUser2()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_2.username

        response = self.app.get('/add_friend/' + user_2.username, follow_redirects=True)
        assert "Friends" in str(response.data)

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

        """
            post a message on the feed
        """

        response = self.app.post('/message/add', data=dict(
            to_user=user_1.username,
            post="Test Post From User 1",
            images=[]
        ), follow_redirects=True)

        assert "Test Post From User 1" in str(response.data)

        """
            write a message to User 2
        """

        response = self.app.post('/message/add', data=dict(
            to_user=user_2.username,
            post="Test Post From User 1 to User 2",
            images=[]
        ), follow_redirects=True)

        assert "Test Post From User 1 to User 2" in str(response.data)

        """
            Login as User 2
        """

        self.app.post('/login', data=dict(
            username=user_2.username,
            password=self.getUser2()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_2.username

        """
            Registeration:  User 3
        """
        user_3 = self.getUser3()
        self.app.post("/register", data=user_3, follow_redirects=True)
        user_3 = User.getByName(username=user_3['username'])
        code = user_3.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_3.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)


        """
            Make a Friendship Request to User 3
        """
        response = self.app.get('/add_friend/' + user_3.username, follow_redirects=True)
        assert "Friendship Requested" in str(response.data)

        """
            Login as User 3
            Confirm Friendship request from User 2
        """

        self.app.post('/login', data=dict(
            username=user_3.username,
            password=self.getUser3()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_3.username

        response = self.app.get('/add_friend/' + user_3.username, follow_redirects=True)
        assert "Friends" in str(response.data)

        """
            Login as User 1
        """

        self.app.post('/login', data=dict(
            username=user_1.username,
            password=self.getUser1()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_1.username

        """
            Block User 3
        """
        response = self.app.get('/block/' + user_3.username, follow_redirects=True)
        assert "Blocked" in str(response.data)

        """
            Login as User 2
        """

        self.app.post('/login', data=dict(
            username=user_2.username,
            password=self.getUser2()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_2.username

        """
            User 2 Confirm User 3
        """

        response = self.app.get('/add_friend/' + user_3.username, follow_redirects=True)
        assert "Friends" in str(response.data)

        """
            write a message to User 3
        """

        response = self.app.post('/message/add', data=dict(
            to_user=user_3.username,
            post="Test Post From User 2 to User 3",
            images=[]
        ), follow_redirects=True)

        assert "Test Post From User 2 to User 3" in str(response.data)

        """
            Login as User 1
        """

        self.app.post('/login', data=dict(
            username=user_1.username,
            password=self.getUser1()['password']
        ))

        with self.app as c:
            c.get('/')
            assert session.get('username') == user_1.username

        """
            Check he doesn't see user 2's post to user 3 (blocked)
        """
        response = self.app.get('/')
        assert "Test Post From User 2 to User 3" not in str(response.data)
