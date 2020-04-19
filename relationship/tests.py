import unittest
import os
from flask import session
from app import create_app as create_app_test
from utils.database import Database
from user.models import User
from relationship.models import Relationship

"""
    NB: To run your tests safely, you should comment sending email operations in the `views.py` file.
"""


class RelationshipTest(unittest.TestCase):

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

    def test_friends_operations(self):
        """
            Registeration:  User 1 & User 2
        """
        user_1 = self.getUser1()
        self.app.post("/register", data=user_1, follow_redirects=True)
        user_1 = User.getByName(username=user_1['username'])
        code = user_1.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_1.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        user_2 = self.getUser2()
        self.app.post("/register", data=user_2, follow_redirects=True)
        user_2 = User.getByName(username=user_2['username'])
        code = user_2.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_2.username + '/' + code)
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
            Add User 2 as Friend
        """
        self.app.get('/add_friend/' + user_2.username)

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
            Check the status of relationship between User 1, User 2.
        """

        status = Relationship.get_relationship_status(user_1, user_2)
        assert status == "FRIENDS_PENDING"

        """
             Accept Friendship from User 1.
        """

        self.app.get('/add_friend/' + user_1.username)

        """
            Check that the relationship between User 1 and  User 2 has been APPROVED
        """

        status = Relationship.get_relationship_status(user_1, user_2)
        assert status == "FRIENDS_APPROVED"

        """
            User 2 Unfriend User 1
        """

        self.app.get('/remove_friend/' + user_1.username)

        assert Relationship.get_relationship(user_2, user_1) is None

        """
            Check that no relationship exist
        """

        assert Database.find('relationships', {}).retrieved == 0

    def test_block_operations(self):
        """
            Registeration:  User 1 & User 2
        """
        user_1 = self.getUser1()
        self.app.post("/register", data=user_1, follow_redirects=True)
        user_1 = User.getByName(username=user_1['username'])
        code = user_1.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_1.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        user_2 = self.getUser2()
        self.app.post("/register", data=user_2, follow_redirects=True)
        user_2 = User.getByName(username=user_2['username'])
        code = user_2.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user_2.username + '/' + code)
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
            User 1 Block User 2
        """

        self.app.get('/block/' + user_2.username)

        """
            Check the relationship status between User 1 and User 2
        """

        status = Relationship.get_relationship_status(user_1, user_2)
        assert status == "BLOCKED"

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
            Check the relationship status between User 2 and User 1
        """

        status = Relationship.get_relationship_status(user_2, user_1)
        assert status == "REVERSE_BLOCKED"

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
            User 1 Unblocks User 2
        """
        self.app.get('/unblock/' + user_2.username)

        """
            Check the relationship status between User 2 and User 1
        """

        status = Relationship.get_relationship_status(user_1, user_2)
        assert status is None # No Relation between user 1 and user 2
