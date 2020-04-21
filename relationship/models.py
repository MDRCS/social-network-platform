import uuid

from user.models import User
from utils.commons import utc_now_timestamp as now
from utils.database import Database

FRIENDS = 1
BLOCKED = -1

RELATIONSHIP_TYPE = {1: 'Friends', -1: 'Blocked'}

PENDING = 0
APPROVED = 1

STATUS_TYPE = {0: 'Pending', 1: 'Approved'}


class Relationship(object):

    def __init__(self, from_user, to_user, _id=None, rel_type=RELATIONSHIP_TYPE.get(FRIENDS),
                 status=STATUS_TYPE.get(PENDING), req_date=now()):

        self.from_user = from_user
        self.to_user = to_user
        self.rel_type = rel_type
        self.status = status
        self.req_date = req_date
        self.meta = Relationship.create_index({"from_user": 1, "to_user": 1})

        self.id = _id if _id else uuid.uuid4().hex

    @staticmethod
    def create_index(indexes):
        return [
            (index, order)
            for index, order in indexes.items()
        ]

    @property
    def username(self):
        return User.getById(self.to_user).username

    def profile_imgsrc(self, size):
        return User.getById(self.to_user).profile_imgsrc(size)

    def is_friend(self, user):
        if user:
            return self.get_relationship_status(user, self.to_user)
        else:
            return None

    def touser(self):
        user = User.getById(self.to_user)
        if user is not None:
            return User(**user)
    @classmethod
    def get_relationship(cls, from_user, to_user):
        rel_record = Database.find_one('relationships', {'from_user': from_user, 'to_user': to_user})
        if rel_record is not None:
            return cls(**rel_record)

    @classmethod
    def get_friends(cls, user, rel_type, status):
        friends_records = Database.find('relationships',
                                        {
                                            "from_user": user,
                                            "rel_type": rel_type,
                                            "status": status
                                        })
        return [cls(**friend) for friend in friends_records]

    @classmethod
    def get_relationship_status(cls, from_user, to_user):
        if from_user == to_user:
            return "SAME"
        rel = Relationship.get_relationship(from_user, to_user)
        if rel and rel.rel_type == RELATIONSHIP_TYPE.get(FRIENDS):
            if rel.status == STATUS_TYPE.get(PENDING):
                return "FRIENDS_PENDING"
            if rel.status == STATUS_TYPE.get(APPROVED):
                return "FRIENDS_APPROVED"
        elif rel and rel.rel_type == RELATIONSHIP_TYPE.get(BLOCKED):
            return "BLOCKED"
        else:
            reverse_rel = Relationship.get_relationship(to_user, from_user)
            if reverse_rel and reverse_rel.rel_type == RELATIONSHIP_TYPE.get(FRIENDS):
                if reverse_rel.status == STATUS_TYPE.get(PENDING):
                    return "REVERSE_FRIENDS_PENDING"
                if reverse_rel.status == STATUS_TYPE.get(APPROVED):
                    return "REVERSE_FRIENDS_APPROVED"
            elif reverse_rel and reverse_rel.rel_type == RELATIONSHIP_TYPE.get(BLOCKED):
                return "REVERSE_BLOCKED"
        return None

    def save_database(self):
        Database.insert('relationships', self.json(), self.meta)

    def update_record(self):
        Database.update('relationships', {'_id': self.id}, {"$set": self.json()})

    def delete_record(self):
        Database.remove('relationships', {'_id': self.id})

    def json(self):
        return {
            "from_user": self.from_user,
            "to_user": self.to_user,
            "rel_type": self.rel_type,
            "status": self.status,
            "req_date": self.req_date,
            "_id": self.id
        }
