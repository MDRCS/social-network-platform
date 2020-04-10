import unittest
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

    def test_register_user(self):
        response = self.app.post("/register", data=dict(
            first_name="Mohamed",
            last_name="El Rahali",
            username="mdrahali",
            email="go@gmail.com",
            password="12345",
            confirm="12345"
        ), follow_redirects=True)

        assert Database.count_record('users', {'username': "mdrahali"}) == 1
