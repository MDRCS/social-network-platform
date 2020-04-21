import uuid
import os
from flask import url_for

from user.models import User
from utils.commons import utc_now_ts_ms as now, linkify, ms_stamp_humanize
from utils.database import Database
from settings import Config

POST = 1
COMMENT = 2
LIKE = 3

MESSAGE_TYPE = {1: 'Post', 2: 'Comment', 3: 'Like'}


class Message(object):

    def __init__(self, from_user, text="", images=[], live=True, createdAt=now(), parent=None,
                 message_type=MESSAGE_TYPE.get(POST), to_user=None, _id=None):
        self.from_user = from_user
        self.to_user = to_user
        self.text = text
        self.live = live
        self.createdAt = createdAt
        self.parent = parent
        self.images = images
        self.message_type = message_type
        self.meta = Message.create_index({"from_user": 1, "to_user": 1, "createdAt": -1, "parent": 1, "live": 1})

        self.id = _id if _id else uuid.uuid4().hex

    @staticmethod
    def create_index(indexes):
        return [
            (index, order)
            for index, order in indexes.items()
        ]

    @classmethod
    def getMessage(cls, message_id):
        message = Database.find_one('messages', {"_id": message_id})
        if message is not None:
            return cls(**message)

    @classmethod
    def getMessages(cls, user, offset=0, limit=10):
        profile_messages = Database.find('messages',
                                         {"message_type": MESSAGE_TYPE.get(POST),
                                          "$or": [{"from_user": user},
                                                  {"to_user": user}]}).sort("createdAt", -1).skip(offset).limit(limit)

        return [cls(**message) for message in profile_messages]

    @property
    def text_linkified(self):
        return linkify(self.text)

    @property
    def human_timestamp(self):
        return ms_stamp_humanize(self.createdAt)

    @property
    def comments(self):
        comments = Database.find('messages', {
                                                "parent": self.id,
                                                "message_type": MESSAGE_TYPE.get(COMMENT)
                                            }).sort("createdAt", -1)
        return [Message(**comment) for comment in comments]

    @property
    def likes(self):
        likes = Database.find('messages', {
            "parent": self.id,
            "message_type": MESSAGE_TYPE.get(LIKE)
        }).sort("createdAt", -1)
        return [Message(**like) for like in likes]

    @property
    def fromUser(self):
        return User.getById(self.from_user)

    @property
    def toUser(self):
        return User.getById(self.to_user)

    def post_imgsrc(self, image_ts, size):
        if Config.AWS_BUCKET:
            return os.path.join(Config.AWS_CONTENT_URL, Config.AWS_BUCKET, 'posts', '%s.%s.%s.png' % (self.id, image_ts, size))
        else:
            return url_for('static',
                           filename=os.path.join(Config.STATIC_IMAGE_URL, 'posts', '%s.%s.%s.png' % (self.id, image_ts, size)))

    def save_database(self):
        Database.insert('messages', self.json(), self.meta)

    def update_record(self):
        Database.update('messages', {'_id': self.id}, {"$set": self.json()})

    def delete_record(self):
        Database.remove('messages', {'_id': self.id})

    def json(self):
        return {
            "from_user": self.from_user,
            "to_user": self.to_user,
            "text": self.text,
            "createdAt": self.createdAt,
            "parent": self.parent,
            "images": self.images,
            "message_type": self.message_type,
            "_id": self.id
        }


# { item : 1, quantity: -1 }

class Feed(object):
    """
        Fan out pattern: means that each user have a list of posts of users that are friends with him (friends_approved).
        So each user have it's feed.
        NB: Fan out pattern is Scalable.
     """

    def __init__(self, user, message, createdAt=now(), _id=None):
        self.user = user
        self.message = message
        self.createdAt = createdAt

        self.meta = Message.create_index({"user": 1, "createdAt": -1})
        self.id = _id if _id else uuid.uuid4().hex

    @staticmethod
    def create_index(indexes):
        return [
            (index, order)
            for index, order in indexes.items()
        ]

    @classmethod
    def get_feed(cls, user):
        feeds = Database.find('feeds', {"user": user}).sort("createdAt", -1).limit(10)
        feeds = [cls(**feed) for feed in feeds]
        for feed in feeds:
            feed.message = Message.getMessage(feed.message)
        return feeds

    @property
    def fromUser(self):
        return User.getById(self.from_user)

    def save_database(self):
        Database.insert('feeds', self.json(), self.meta)

    def update_record(self):
        Database.update('feeds', {'_id': self.id}, {"$set": self.json()})

    def delete_record(self):
        Database.remove('feeds', {'_id': self.id})

    def json(self):
        return {
            "user": self.user,
            "message": self.message,
            "createdAt": self.createdAt,
            "_id": self.id
        }

