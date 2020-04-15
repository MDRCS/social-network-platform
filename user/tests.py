import unittest
import os
import bcrypt
from flask import session
from app import create_app as create_app_test
from utils.database import Database
from user.models import User
from settings import config


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

        # save same email
        # use a username already used
        user = self.getUser()
        user['email'] = "mdr.ga99@example.com"

        response = self.app.post('/edit', data=user, follow_redirects=True)

        assert "This email is already in use." in str(response.data)

    def test_get_profile(self):
        user = self.getUser()
        self.app.post("/register", data=user, follow_redirects=True)
        user = User.getByName(username=self.getUser()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        self.app.post('/login', data=dict(
            username=user.username,
            password=self.getUser()['password']
        ))

        response = self.app.get('/profile/' + user.username)
        assert "@" + user.username in str(response.data)

    def test_forget_password(self):
        # create user
        user = self.getUser()
        self.app.post("/register", data=user, follow_redirects=True)
        user = User.getByName(username=self.getUser()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        user = self.getUser()
        response = self.app.post('/forgot', data=user)
        assert "You will receive a password reset email if we find that email in our system" in str(response.data)

        user = User.getByName(username=self.getUser()['username'])
        assert user.change_configuration != {}

        user_passwords = {
            "current_password": user.password,
            "password": "12346",
            "confirm": "12346"
        }

        self.app.post(
                        '/password_reset/' + user.username + '/'
                        + user.change_configuration['password_reset_code'],
                        data=user_passwords
        )

        user = User.getByName(username=self.getUser()['username'])

        assert bcrypt.hashpw(user_passwords['password'], user.password) == user.password
        assert bcrypt.checkpw(user_passwords['password'], user.password)
        response = self.app.get('/password_reset_complete')

        assert "Your password has been updated" in str(response.data)

        # logging with new password

        response = self.app.post('/login', data=dict(
            username=user.username,
            password=user_passwords['password']
        ))

        assert response.status_code == 200
        with self.app as c:
            c.get('/')
            assert session['username'] == user.username
