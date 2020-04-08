import uuid
from flask import session
from utils.commons import utc_now_timestamp as now
from utils.database import Database


# user = User(username='mdrahali', password='123', email='mdr.ga99@gmail.com', first_name='Mohamed', last_name='El Rahali', bio='bio ...')


class User(object):

    def __init__(self, username, password, email, first_name, last_name, createdAt=None, _id=None):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.createdAt = createdAt if createdAt else now()
        self.id = _id if _id else uuid.uuid4().hex
        self.meta = User.create_index({"username": 1, "email": 1, "createdAt": -1})

    @classmethod
    def create_index(cls, indexes):
        return [
            (index, order)
            for index, order in indexes.items()
        ]

    @classmethod
    def getByEmail(cls, email):
        user = Database.find_one('users', {'email': email})
        if user is not None:
            return cls(**user)

    @classmethod
    def getByName(cls, username):
        user = Database.find_one('users', {'username': username})
        if user is not None:
            return cls(**user)

    @classmethod
    def getById(cls, id):
        user = Database.find_one('users', {'id': id})
        if user is not None:
            return cls(**user)

    @staticmethod
    def valid_login(email, password):
        # check whether a user's email matches the password that they sent us
        user = User.getByEmail(email)
        if user is not None:
            return user.password == password
        return False

    @staticmethod
    def login(user_email):
        # valid_login() has already been called
        session['email'] = user_email

    @staticmethod
    def logout(user_email):
        session['email'] = None

    @classmethod
    def register(cls, email, password):
        user = cls.getByEmail(email)
        if user is None:
            new_user = cls(email, password)
            new_user.save_database()
            session['email'] = email
            return True
        else:
            return False

    def save_database(self):
        Database.insert('users', self.json(), self.meta)

    def json(self):
        return {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "createdAt": self.createdAt,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "_id": self.id,
        }
