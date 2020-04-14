import unittest
import os
from flask import session
from app import create_app as create_app_test
from utils.database import Database
from user.models import User


class UserTest(unittest.TestCase):

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

    def getUser(self):
        return dict(
            first_name="Mohamed",
            last_name="El Rahali",
            username="mdrahali",
            email="elrahali.md@gmail.com",
            password="12345",
            confirm="12345"
        )

    def test_register_user(self):
        """
            Basic Registration Test
        """
        self.app.post("/register", data=self.getUser(), follow_redirects=True)
        user = User.getByName("mdrahali")
        user.email_confirmation = True
        user.change_configuration = {}
        user.update_record()
        assert Database.count_record('users', {'username': "mdrahali"}) == 1
        """
            Invalid Username
        """
        invalid_user = self.getUser()
        invalid_user['username'] = "wrong wrong"
        response = self.app.post("/register", data=invalid_user, follow_redirects=True)

        assert "Username must contain only letters numbers or underscore" in str(response.data)

    def test_login_user(self):
        self.app.post("/register", data=self.getUser(), follow_redirects=True)
        user = User.getByName(username=self.getUser()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)
        # try again to confirm
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert rv.status_code == 404

        response = self.app.post('/login', data=dict(
            username=user.username,
            password=self.getUser()['password']
        ))

        with self.app as c:  # Each time you want to use a session map you should follow this method
            c.get('/')
            assert response.status_code == 200
            assert session['username'] == user.username

    def test_edit_profile(self):
        self.app.post("/register", data=self.getUser(), follow_redirects=True)
        user = User.getByName(username=self.getUser()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        response = self.app.post('/login', data=dict(
            username=user.username,
            password=self.getUser()['password']
        ))

        response = self.app.get('/edit')
        assert response.status_code == 200

        # Edit First Name
        user = self.getUser()
        user['first_name'] = "Test First Name"

        response = self.app.post('/edit', data=user, follow_redirects=True)

        assert "Your info has been updated succefully ..!" in str(response.data)
        assert "Test First Name" == User.getByName(user['username']).first_name

        # Edit username & email
        user = self.getUser()
        user['username'] = "kaka123"
        user['email'] = "mdr.ga99@example.com"

        response = self.app.post('/edit', data=user, follow_redirects=True)

        user = User.getByName(username=user['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        self.app.post('/login', data=dict(
            username=user.username,
            password=self.getUser()['password']
        ))

        assert "kaka123" == User.getByName(user.username).username
        assert "mdr.ga99@example.com" == User.getByName(user.username).email

        # Second User
        self.app.post("/register", data=self.getUser(), follow_redirects=True)
        user = User.getByName(username=self.getUser()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        response = self.app.post('/login', data=dict(
            username=user.username,
            password=self.getUser()['password']
        ))

        assert response.status_code == 200

        # use a username already used
        user = self.getUser()
        user['username'] = "kaka123"
        response = self.app.post('/edit', data=user, follow_redirects=True)

        assert "This username is already in use." in str(response.data)

        with self.app as c:
            c.get('/')
            print(session['username'])

        for u in Database.find('users', {}):
            print(u)

        # save same email
        # use a username already used
        user = self.getUser()
        user['email'] = "mdr.ga99@example.com"

        response = self.app.post('/edit', data=user, follow_redirects=True)

        assert "This email is already in use." in str(response.data)
