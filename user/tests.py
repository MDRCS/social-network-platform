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
            Invalid
        """
        invalid_user = self.getUser()
        invalid_user['username'] = "wrong wrong"
        response = self.app.post("/register", data=invalid_user, follow_redirects=True)
        print(str(response.data))
        # assert "Invalid Username" in str(response.data)

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

