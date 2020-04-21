from feed.models import Message, Feed
from relationship.models import Relationship, RELATIONSHIP_TYPE, STATUS_TYPE, FRIENDS, APPROVED, PENDING, BLOCKED
from user.models import User


def process_message(message):

    # get the from_user friends
    from_user = User.getById(message.from_user)
    friends = Relationship.get_friends(
        user=from_user.id,
        rel_type=RELATIONSHIP_TYPE.get(FRIENDS),
        status=STATUS_TYPE.get(APPROVED)
    )

    """
        Fan out pattern: means that each user have a list of posts of users that are friends with him (friends_approved).
        So each user have it's feed.
        NB: Fan out pattern is Scalable.
    """

    # get the from_user's friends
    for friend in friends:
        rel_status = Relationship.get_relationship_status(friend.to_user, message.to_user)
        if rel_status != "BLOCKED":
            Feed(
                user=friend.to_user,
                message=message.id,
            ).save_database()

    return True
