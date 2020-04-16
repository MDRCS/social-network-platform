import uuid
import os
from flask import session, url_for
from utils.commons import utc_now_timestamp as now
from utils.database import Database
from settings import Config


class User(object):

    def __init__(self, username, password, email, first_name, last_name, bio, profile_image="",
                 email_confirmation=False, change_configuration={}, createdAt=None, _id=None):
        self.username = username.lower()
        self.password = password
        self.email = email.lower()
        self.first_name = first_name
        self.last_name = last_name
        self.createdAt = createdAt if createdAt else now()
        self.id = _id if _id else uuid.uuid4().hex
        self.bio = bio
        self.profile_image = profile_image
        self.meta = User.create_index({"username": 1, "email": 1, "createdAt": -1})
        self.email_confirmation = email_confirmation
        self.change_configuration = change_configuration

    @classmethod
    def create_index(cls, indexes):
        return [
            (index, order)
            for index, order in indexes.items()
        ]

    def profile_imgsrc(self, size):
        if self.profile_image:
            if Config.AWS_BUCKET:
                print(os.path.join(Config.AWS_CONTENT_URL, Config.AWS_BUCKET, 'user',
                                    '%s.%s.%s.png' % (self.id, self.profile_image, size)))
                return os.path.join(Config.AWS_CONTENT_URL, Config.AWS_BUCKET, 'user',
                                    '%s.%s.%s.png' % (self.id, self.profile_image, size))
            else:
                return url_for('static', filename=os.path.join(Config.STATIC_IMAGE_URL, 'user',
                                                               '%s.%s.%s.png' % (self.id, self.profile_image, size)))
        else:
            return url_for('static', filename=os.path.join(Config.STATIC_IMAGE_URL, 'user', 'no-profile.%s.png' % (size)))

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
    def logout():
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

    def update_record(self):
        Database.update('users', {'_id': self.id}, {"$set": self.json()})

    def json(self):
        return {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "createdAt": self.createdAt,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "email_confirmation": self.email_confirmation,
            "change_configuration": self.change_configuration,
            "profile_image": self.profile_image,
            "_id": self.id,
        }
