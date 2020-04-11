import unittest
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
        self.db_name = self.app_factory.config['MONGODB_NAME']
        self.app = self.app_factory.test_client()

    def tearDown(self) -> None:
        db = Database.CLIENT
        db.drop_database(self.db_name)

    def getUser(self):
        return dict(
            first_name="Mohamed",
            last_name="El Rahali",
            username="mdrahali",
            email="go@gmail.com",
            password="12345",
            confirm="12345"
        )

    def test_register_user(self):
        """
            Basic Registration Test
        """
        _ = self.app.post("/register", data=self.getUser(), follow_redirects=True)
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
        response = self.app.post('/login', data=dict(
            username=self.getUser()['username'],
            password=self.getUser()['password']
        ))

        with self.app as c:  # Each time you want to use a session map you should follow this method
            _ = c.get('/')
            assert response.status_code == 200
            assert session['username'] == self.getUser()['username']

    def test_edit_profile(self):
        user = self.getUser()
        self.app.post("/register", data=self.getUser(), follow_redirects=True)

        # Check `Edit profile` feature
        _ = self.app.post('/login', data=dict(
            username=user['username'],
            password=user['password']
        ))

        response = self.app.get('/edit')
        assert response.status_code == 200

        user['first_name'] = "Test First Name"

        # Edit Profile
        response = self.app.post('/edit', data=user)
        assert "Your info has been updated succefully ..!" in str(response.data)
        assert "Test First Name" == User.getByName(user['username']).first_name

        user = self.getUser()
        user['username'] = "kaka123"
        user['email'] = "ex@example.com"
        self.app.post("/register", data=user, follow_redirects=True)

        _ = self.app.post('/login', data=dict(
            username=user['username'],
            password=user['password']
        ))

        # use a username already used
        user['username'] = 'mdrahali'
        response = self.app.post('/edit', data=user)

        assert "This username is already in use." in str(response.data)

        # try to save same email
        # use a username already used
        user['email'] = 'go@gmail.com'
        response = self.app.post('/edit', data=user)

        assert "This email is already in use." in str(response.data)
